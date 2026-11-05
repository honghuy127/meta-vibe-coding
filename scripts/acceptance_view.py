"""Read-only replay of a finished acceptance run. No agent, inference or live product app.

    acceptance_view.py --plan PLAN --run-dir DIR

Then open http://127.0.0.1:8012/?job=N01-wrapper&stage=-1 . Controls are disabled and
original HTTP statuses, not this page, establish export gating. See D014.
"""
import argparse
import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, Response

PORT = 8012
BASELINE_PAGE = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Transcript baseline replay</title>'
    '<link rel="stylesheet" href="/style.css"><script src="/baseline.js" defer></script></head><body><main>'
    '<h1>Transcript baseline replay</h1><p id="status"></p><h2>Owner View</h2><pre id="owner"></pre>'
    '<h2>Developer View</h2><pre id="brief"></pre></main></body></html>')
BASELINE_SCRIPT = """fetch('/review/snapshot'+location.search).then(r=>r.json()).then(s=>{
const b=s.baseline;
document.getElementById('owner').textContent=b?b.owner_view:'No accepted response was recorded.';
document.getElementById('brief').textContent=b?JSON.stringify(b.developer_view,null,2):'No current accepted brief.';
document.getElementById('status').textContent=s.failure?'Recorded failure: '+(s.failure.message||s.failure.code)+'. '+(b?'The response below is outdated, not a current result.':'No accepted result is available.'):'Read-only transcript baseline replay; no wrapper state or inference.';
});"""
WRAPPER_SCRIPT = """
replayConfigReady.then(async()=>{
 const snap=await fetch('/review/snapshot'+location.search).then(r=>r.json());
 state=snap.state;previousResult=snap.previous_valid;configured=false;await render();
 for(const id of ['start','reset','reply','unknown','provisional','revise','retry'])$(id).disabled=true;
 document.querySelector('details').open=true;$('agent').textContent='Recorded HTTP replay';
 $('download').textContent='Download recorded brief';$('usage').textContent='No coding-agent call is available.';
 status(snap.failure?'Recorded failure: '+snap.failure.message:'Recorded HTTP replay; disabled controls do not establish live export gating.');
});
"""


def records(run_dir: Path) -> dict:
    """Rows per closed job, one per recorded stage. Open jobs stay invisible."""
    events = [json.loads(line) for line in (run_dir / 'journal.jsonl').read_bytes().splitlines()]
    rows = {}
    for final in (event for event in events if event['type'] == 'job_finished'):
        job = final['job']
        if job.endswith('-wrapper'):
            advances = [e for e in events if e['type'] == 'http' and e.get('job') == job and e['path'] == '/api/advance']
            exports = [e for e in events if e['type'] == 'http' and e.get('job') == job and e['path'] == '/api/export']
            if len(advances) != len(exports):
                raise ValueError('Paired recorded HTTP responses required.')
            previous, rows[job] = None, []
            for index, (advance, export) in enumerate(zip(advances, exports)):
                state = advance['response']['state']
                rows[job].append({'job': job, 'stage': index + 1, 'state': state, 'previous_valid': previous,
                    'export': export, 'failure': advance['response']['error']})
                if state.get('assessment'):
                    previous = state
        else:
            accepted = [e['result'] for e in events if e['type'] == 'baseline_result' and e.get('job') == job]
            rows[job] = [{'job': job, 'stage': index + 1, 'baseline': result, 'failure': None} for index, result in enumerate(accepted)]
            if final['failure']:
                rows[job].append({'job': job, 'stage': len(rows[job]) + 1, 'baseline': accepted[-1] if accepted else None,
                    'failure': final['failure'], 'outdated': True})
    return rows


def create_app(plan_path: Path, run_dir: Path) -> FastAPI:
    source = json.loads(plan_path.read_text())['frozen_runtime']['source_snapshot']
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware('http')
    async def boundary(request: Request, call_next):
        host = request.headers.get('host', '')
        if host.split(':')[0] not in {'127.0.0.1', 'localhost', 'testserver'}:
            return JSONResponse({'error': 'Local review only'}, 403)
        if request.method == 'POST' and request.headers.get('origin') not in (None, f'{request.url.scheme}://{host}'):
            return JSONResponse({'error': 'Cross-origin rejected'}, 403)
        response = await call_next(request)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Content-Security-Policy'] = ("default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; "
            "object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        return response

    @app.get('/')
    async def page(job: str, stage: int = -1):
        if job not in records(run_dir):
            return HTMLResponse('No closed attempt', 404)
        html = source['src/meta_vibe_coding/static/index.html'] if job.endswith('-wrapper') else BASELINE_PAGE
        return HTMLResponse(html.replace('<body>', '<body><p>Recorded HTTP replay: no live owner interaction or coding-agent calls. Any download is a replay download.</p>', 1))

    @app.get('/review/snapshot')
    async def snapshot(job: str, stage: int = -1):
        rows = records(run_dir).get(job)
        if not rows:
            return JSONResponse({'error': 'No recorded result'}, 404)
        index = len(rows) - 1 if stage == -1 else stage - 1
        if not 0 <= index < len(rows):
            return JSONResponse({'error': 'No recorded stage'}, 404)
        return rows[index]

    @app.get('/api/config')
    async def config():
        return {'agent': 'recorded-replay', 'enabled': False, 'requested_model': None,
            'data_notice': 'Recorded fictional data only; no coding agent connected.', 'allowance_notice': 'No native allowance in this viewer.'}

    @app.get('/style.css')
    async def style():
        return Response(source['src/meta_vibe_coding/static/style.css'], media_type='text/css')

    @app.get('/app.js')
    async def script():
        code, anchor = source['src/meta_vibe_coding/static/app.js'], "fetch('/api/config').then("
        if code.count(anchor) != 1:
            raise ValueError('Controller startup changed.')
        return Response(code.replace(anchor, 'const replayConfigReady = ' + anchor) + WRAPPER_SCRIPT, media_type='application/javascript')

    @app.get('/baseline.js')
    async def baseline():
        return Response(BASELINE_SCRIPT, media_type='application/javascript')

    @app.post('/api/export')
    async def export(request: Request):
        body = await request.json()
        for stages in records(run_dir).values():
            for row in stages:
                if 'state' in row and json.dumps(body, sort_keys=True) == json.dumps(row['state'], sort_keys=True):
                    return JSONResponse(row['export']['response'], row['export']['status'])
        return JSONResponse({'error': 'Only exact recorded wrapper snapshots can be exported'}, 409)

    @app.post('/api/start')
    @app.post('/api/advance')
    async def blocked():
        return JSONResponse({'error': 'Read-only recorded replay; inference unavailable'}, 410)
    return app


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--run-dir', type=Path, required=True)
    args = parser.parse_args()
    import uvicorn
    uvicorn.run(create_app(args.plan, args.run_dir), host='127.0.0.1', port=PORT, access_log=False)
