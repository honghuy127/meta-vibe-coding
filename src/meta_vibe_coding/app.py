"""Local HTTP interface; reasoning is delegated to one coding agent."""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError
from starlette.middleware.trustedhost import TrustedHostMiddleware

from .agents import AGENTS, Agent, CodingAgent
from .core import FlowError, adopt, charge, check_allowance, export_brief, prepare
from .models import IDEA_ASSESSMENTS, AdvanceRequest, Model, State, Text
from .settings import load_limits


class StartRequest(Model):
    idea: Text


def create_app(agent: Agent | None = None) -> FastAPI:
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost", "[::1]", "testserver"])
    limits = load_limits()
    adapter = agent if agent is not None else CodingAgent(limits=limits)

    @app.middleware("http")
    async def local_boundary(request: Request, call_next):
        if request.method == "POST":
            origin = request.headers.get("origin")
            expected = f"{request.url.scheme}://{request.headers.get('host', '')}"
            if origin and origin != expected:
                return JSONResponse({"error": "Cross-origin requests are not allowed"}, status_code=403)
            if request.headers.get("content-type", "").split(";")[0] != "application/json":
                return JSONResponse({"error": "Use application/json"}, status_code=415)
            if len(await request.body()) > 128_000:
                return JSONResponse({"error": "Request is too large"}, status_code=413)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @app.exception_handler(ValidationError)
    async def invalid_candidate(_request, _exc):
        return JSONResponse({"error": "State validation failed", "code": "invalid_output"}, status_code=422)

    # Avoid echoing user input or validation payloads in HTTP errors.
    from fastapi.exceptions import RequestValidationError

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_request, _exc):
        return JSONResponse({"error": "Invalid request or state", "code": "invalid_input"}, status_code=422)

    @app.get("/api/config")
    async def config():
        return {"agent": getattr(adapter, "agent", "test-double"),
                "requested_model": getattr(adapter, "model", None),
                "enabled": getattr(adapter, "enabled", True), "implemented_agents": list(AGENTS),
                "limits": {"request_seconds": limits.request_seconds, "session_seconds": limits.session_seconds,
                           "idea_assessments": IDEA_ASSESSMENTS, "server_calls": getattr(adapter, "max_calls", None)},
                "data_notice": "Your idea and replies go through this coding agent to its configured model. That may be local or remote. The agent and provider may retain transcripts; use fictional inputs during prototype review.",
                "allowance_notice": f"Each idea can be assessed up to {IDEA_ASSESSMENTS} times. Separately, this server allows at most {getattr(adapter, 'max_calls', IDEA_ASSESSMENTS)} agent calls in total until it is restarted; a new idea does not reset that. Model usage and billing belong to the selected agent; this app does not enforce a dollar budget."}

    @app.post("/api/start")
    async def start(body: StartRequest):
        return State(raw_intent=body.idea).model_dump()

    @app.post("/api/advance")
    async def advance(body: AdvanceRequest):
        try:
            state = prepare(body)
        except FlowError as exc:
            return JSONResponse({"code": exc.code, "error": exc.message}, status_code=422)

        def reply(state: State, usage=None, error: FlowError | None = None) -> dict:
            return {"request_id": body.request_id, "state": state.model_dump(),
                    "usage": usage.model_dump() if usage else None, "error": error.payload() if error else None,
                    "server_calls_left": getattr(adapter, "calls_left", None)}

        try:
            check_allowance(state, limits)
            candidate, usage = await adapter.assess(state, body.provisional)
        except FlowError as exc:
            return reply(charge(state) if exc.charged() else state, error=exc)
        state = charge(state)
        try:
            return reply(adopt(state, candidate, allow_question=not body.provisional), usage)
        except FlowError as exc:
            return reply(state, error=exc)
        except ValidationError:
            return reply(state, error=FlowError("invalid_output", "The agent result failed state validation. Your answers are retained."))

    @app.post("/api/export")
    async def export(state: State):
        try:
            return export_brief(state)
        except FlowError as exc:
            return JSONResponse({"code": exc.code, "error": exc.message}, status_code=409)

    app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="ui")
    return app


app = create_app()
