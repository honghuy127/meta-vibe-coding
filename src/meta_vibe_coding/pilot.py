"""Opt-in fictional pilot server; a default invocation only checks the saved cooldown."""

import argparse
import asyncio
import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def pilot_plan(record: dict, now: float | None = None) -> dict:
    cap = record["authority"]["additional_spend_cap_usd"]
    if record.get("kind") != "fictional-development-pilot" or type(cap) is not int or cap != 0:
        raise ValueError("Expected a fictional pilot record with $0 additional-spend authority.")
    model = record["agent"]["requested_model"]
    if record["agent"].get("name") != "opencode" or not isinstance(model, str) or not model.startswith("opencode/") or not model.endswith("-free"):
        raise ValueError("This pilot runner requires the recorded OpenCode free-model selector.")
    allowance = record["authority"]["native_invocation_limit"]
    if type(allowance) is not int or not 1 <= allowance <= 7:
        raise ValueError("The recorded invocation allowance must be between one and seven.")
    request_ids = [attempt["request"]["request_id"] for attempt in record["attempts"]]
    if not request_ids or any(not isinstance(value, str) or not value for value in request_ids) or len(set(request_ids)) != len(request_ids):
        raise ValueError("A continuation requires unique recorded assessment request IDs.")
    retry_at = 0
    for attempt in record["attempts"]:
        for line in (attempt.get("native_stdout") or "").splitlines():
            event = json.loads(line)
            if not isinstance(event, dict) or event.get("type") != "error":
                continue
            error = event.get("error")
            if not isinstance(error, dict) or error.get("type") != "provider.free-limit":
                continue
            timestamp, delay = event["timestamp"], error["retryAfterMs"]
            if any(type(value) is not int or value < 0 for value in (timestamp, delay)):
                raise ValueError("Invalid native quota timestamp or retry delay.")
            retry_at = max(retry_at, (timestamp + delay) / 1000)
    remaining = max(0, allowance - len(record["attempts"]))
    waiting = (time.time() if now is None else now) < retry_at
    return {"status": "allowance_exhausted" if not remaining else "cooldown" if waiting else "pricing_check_required",
            "continuation_id": hashlib.sha256(json.dumps(request_ids).encode()).hexdigest(),
            "requested_model": model, "remaining_invocations": remaining,
            "retry_not_before_utc": datetime.fromtimestamp(retry_at, timezone.utc).isoformat() if retry_at else None,
            "notice": "The saved quota deadline applies to the recorded routing context, not every native session. Recheck native workspace settings and current free pricing before starting. Use fictional inputs only."}


def configure_pilot(plan: dict) -> dict:
    model = plan["requested_model"]
    overlay = {"model": model,
        "agents": {name: {"model": model} for name in ("title", "summary", "compaction")},
        "warming": False, "compaction": {"auto": False},
        "experimental": {"background_compaction": False},
        "policies": [{"action": "provider.use", "resource": "*", "effect": "deny"},
                     {"action": "provider.use", "resource": "opencode", "effect": "allow"},
                     {"action": "tool.use", "resource": "*", "effect": "deny"}]}
    os.environ.update(MVC_AGENT="opencode", MVC_ENABLE_AGENT="1", MVC_AGENT_MODEL=model,
        MVC_AGENT_ENV="", MVC_AGENT_MAX_CALLS=str(plan["remaining_invocations"]),
        MVC_REQUEST_TIMEOUT_SECONDS="300", MVC_SESSION_TIMEOUT_SECONDS="1800",
        OPENCODE_CONFIG_CONTENT=json.dumps(overlay))
    return overlay


def native_routing_config(catalog: dict, model: str) -> dict:
    """Use resolved native metadata, never the redacted debug-config representation."""
    provider, model_id = model.split("/", 1)
    matches = [row for row in catalog["data"] if row.get("providerID") == provider and row.get("modelID") == model_id]
    if len(matches) != 1:
        raise ValueError("The selected model must resolve uniquely in the native session.")
    workspace = matches[0].get("headers", {}).get("x-opencode-org-id")
    if not isinstance(workspace, str) or not re.fullmatch(r"(?:wrk|org)_[A-Za-z0-9]+", workspace) or "redact" in workspace.lower():
        raise ValueError("Native workspace routing is missing, redacted or unsupported; no config was exported.")
    return {"providers": {provider: {"headers": {"x-opencode-org-id": workspace}}}}


def export_native_routing(model: str, output: Path) -> None:
    from .agents import agent_environment
    from .process import run_cli

    env = agent_environment("opencode")
    env["PWD"] = str(Path.home())
    raw = asyncio.run(run_cli(["opencode", "api", "GET", "/api/model"], content="", cwd=str(Path.home()), env=env, timeout=30))
    config = native_routing_config(json.loads(raw), model)
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as file:
        json.dump(config, file)


def record_app(journal, agent=None):
    from fastapi.responses import Response

    from .app import create_app

    app = create_app(agent)

    @app.middleware("http")
    async def capture(request, call_next):
        if request.method != "POST" or request.url.path not in {"/api/start", "/api/advance", "/api/export"}:
            return await call_next(request)
        exchange_id = str(uuid4())
        journal.write(json.dumps({"type": "http_started", "exchange_id": exchange_id,
            "at_utc": datetime.now(timezone.utc).isoformat(), "path": request.url.path}) + "\n")
        journal.flush()
        body = await request.body()
        response = await call_next(request)
        raw = b"".join([chunk async for chunk in response.body_iterator])
        # Invalid requests may contain unrelated data; record only the app's safe error.
        payload = json.loads(body) if response.status_code < 400 else None
        try:
            result = json.loads(raw)
        except (ValueError, UnicodeError):
            result = {"error": "Non-JSON response omitted from pilot evidence."}
        entry = {"type": "http", "exchange_id": exchange_id, "at_utc": datetime.now(timezone.utc).isoformat(),
            "path": request.url.path, "request": payload,
            "status": response.status_code, "response": result}
        journal.write(json.dumps(entry, ensure_ascii=False) + "\n")
        journal.flush()
        return Response(raw, status_code=response.status_code, headers=dict(response.headers),
                        background=response.background)

    return app


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=Path("artifacts/2026-10-29-opencode-free-pilot.json"))
    parser.add_argument("--serve", action="store_true", help="Enable the local pilot for fictional inputs only.")
    parser.add_argument("--free-pricing-checked", action="store_true", help="Confirm the exact recorded model is still free; not a dollar cap.")
    parser.add_argument("--recheck-after-login", action="store_true", help="Explicitly retry after a changed native login, before the old cooldown expires; keeps the existing call allowance.")
    parser.add_argument("--export-native-routing", type=Path, help="Export resolved native home-session workspace routing to a new private config file, without inference or credential export.")
    parser.add_argument("--output", type=Path, help="New local JSONL evidence file; existing files are never overwritten.")
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args(argv)
    if args.serve and args.export_native_routing:
        parser.error("Export native routing separately from serving the pilot.")
    seed_bytes = args.record.read_bytes()
    record = json.loads(seed_bytes)
    plan = pilot_plan(record)
    print(json.dumps(plan, indent=2))
    if args.export_native_routing:
        export_native_routing(plan["requested_model"], args.export_native_routing)
        print("Native routing exported privately. Treat its contents as private and reference it through OPENCODE_CONFIG.")
        return 0
    if not args.serve:
        return 0
    login_recheck = args.recheck_after_login and plan["status"] == "cooldown"
    if plan["status"] != "pricing_check_required" and not login_recheck:
        print("Pilot not started: the recorded cooldown or invocation allowance blocks this run.")
        return 2
    if not args.free_pricing_checked:
        parser.error("Recheck current free pricing, then pass --free-pricing-checked explicitly.")
    if not 1 <= args.port <= 65535:
        parser.error("--port must be between 1 and 65535.")
    overlay = configure_pilot(plan)
    output = args.output or Path("/tmp") / datetime.now(timezone.utc).strftime("meta-vibe-pilot-%Y%m%dT%H%M%SZ.jsonl")
    claim = args.record.with_name(".pilot-" + plan["continuation_id"] + ".claim")
    try:
        descriptor = os.open(claim, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        print("Pilot not started: this seed was already claimed. Review its evidence and reconcile attempts/cooldowns before another launch.")
        return 2
    # Reserve the whole continuation once, including concurrent starts and failed launches.
    with os.fdopen(descriptor, "w") as marker:
        marker.write(json.dumps({"evidence": str(output.resolve()), "reserved_invocations": plan["remaining_invocations"],
            "at_utc": datetime.now(timezone.utc).isoformat()}) + "\n")
    # Exclusive creation and private permissions keep evidence local and preserve prior runs.
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, "w") as journal:
        package = Path(__file__).parent
        hashes = {str(path.relative_to(package)): hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in sorted(package.rglob("*"))
                  if path.suffix in {".py", ".txt", ".js", ".html", ".css"}}
        journal.write(json.dumps({"type": "manifest", "format_version": 1,
            "kind": "fictional-development-pilot", "plan": plan, "native_overlay": overlay,
            "baseline_source_commit": record["source_commit"],
            "continuation_claim": claim.name,
            "seed_record_sha256": hashlib.sha256(seed_bytes).hexdigest(),
            "runtime_source_sha256": hashes, "operator_free_pricing_checked": True,
            "operator_changed_login_recheck": login_recheck,
            "native_config_reference_present": bool(os.getenv("OPENCODE_CONFIG")),
            "capture_limits": "HTTP inputs, validated results, export responses and safe errors only; no raw CLI events, browser observations, or independent billing/retention checks. Source hashes identify the working files; the baseline commit may exclude uncommitted changes."}) + "\n")
        journal.flush()
        app = record_app(journal)
        print(f"Fictional pilot: http://127.0.0.1:{args.port}; evidence: {output}")
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=args.port, access_log=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
