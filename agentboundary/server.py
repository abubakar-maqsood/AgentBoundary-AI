import os, re, secrets, threading, time, uuid
from collections import deque
from datetime import datetime, timezone, timedelta
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field
from .core import Store, permit
from .inference import generate, explain_output
from .runner import Sandbox

BASE=Path(__file__).resolve().parent
DATA=Path(os.environ.get('AB_DATA_DIR',BASE.parent/'data'))
DATA.mkdir(parents=True,exist_ok=True)
KEY=os.environ.get('AB_AUDIT_KEY','local-development-key-not-for-production')
store=Store(str(DATA/'events.sqlite3'),KEY)
runner=Sandbox()
app=FastAPI(title='AgentBoundary Agent Rush',docs_url=None,redoc_url=None,openapi_url=None)
security=HTTPBasic(auto_error=False)
lock=threading.Lock()

class Goal(BaseModel):
    goal:str=Field(min_length=8,max_length=650)

async def auth(request:Request, creds:HTTPBasicCredentials|None=Depends(security)):
    configured=os.environ.get('AB_DEMO_PASSWORD')
    if not configured:
        raise HTTPException(503,'Set AB_DEMO_PASSWORD before using this service')
    good=(creds is not None and secrets.compare_digest(creds.username.encode(),os.environ.get('AB_DEMO_USER','judge').encode())
          and secrets.compare_digest(creds.password.encode(),configured.encode()))
    if not good:raise HTTPException(401,'Authentication required',headers={'WWW-Authenticate':'Basic realm="AgentBoundary"'})
    if request.method not in ('GET','HEAD'):
        # Require a same-origin custom header to prevent cross-origin form posts.
        if request.headers.get('X-AgentBoundary-UI')!='1':raise HTTPException(403,'Missing same-origin request marker')
        origin=request.headers.get('origin')
        public=os.environ.get('AB_PUBLIC_ORIGIN','').rstrip('/')
        if origin and public and origin.rstrip('/')!=public:raise HTTPException(403,'Origin mismatch')

@app.get('/admin',response_class=HTMLResponse)
async def homepage(_:None=Depends(auth)):
    return (BASE/'ui.html').read_text(encoding='utf-8')

@app.get('/healthz')
async def health():return {'status':'ok','service':'agentboundary','mode':'fixture' if os.environ.get('LOCAL_FIXTURE_MODE')=='1' else 'vultr'}

@app.post('/api/tasks')
def plan(body:Goal,_:None=Depends(auth)):
    if not lock.acquire(blocking=False):raise HTTPException(429,'Another task is being processed; retry')
    try:
        try: steps,model=generate(body.goal)
        except Exception as e: raise HTTPException(502, 'Inference unavailable: '+str(e)[:180])
        task=store.add(body.goal,steps)
        store.log(task['id'],'PLAN_READY','Two-step plan received from '+model)
        return {'task':public_task(task),'inference_model':model}
    finally:lock.release()

def public_task(t):
    # Only expose the user's own task; access controlled by shared demo password.
    return {k:v for k,v in t.items() if k!='steps'}|{'steps':[{'name':s['name'],'reason':s['reason'],
      'code_sha256':__import__('hashlib').sha256(s['code'].encode()).hexdigest()} for s in t['steps']]}

@app.get('/api/tasks/{task_id}')
async def read(task_id:str,_:None=Depends(auth)):
    task=store.get(task_id)
    if not task:raise HTTPException(404,'Task not found')
    return {'task':public_task(task),'events':store.events(task_id),'audit_integrity':store.audit_valid()}

@app.post('/api/tasks/{task_id}/revoke')
async def revoke(task_id:str,_:None=Depends(auth)):
    task=store.get(task_id)
    if not task:raise HTTPException(404,'Task not found')
    store.update(task_id,revoked=1)
    store.log(task_id,'PERMISSION_REVOKED','Task permission revoked; subsequent steps denied')
    return {'status':'revoked'}

@app.post('/api/tasks/{task_id}/execute-next')
def execute(task_id:str,_:None=Depends(auth)):
    if not lock.acquire(blocking=False):raise HTTPException(429,'Execution currently busy')
    try:
        task=store.get(task_id)
        if not task:raise HTTPException(404,'Task not found')
        permitted,why=permit(task,task['step_index'])
        if not permitted:
            store.log(task_id,'POLICY_DENIED',why)
            return {'decision':'BLOCK','reason':why}
        index=task['step_index'];step=task['steps'][index]
        store.log(task_id,'STEP_AUTHORIZED','Step '+str(index+1)+' authorized')
        store.update(task_id,state='running')
        try: result=runner.execute(step['code'])
        except Exception as e:
            store.update(task_id,state='error');store.log(task_id,'SANDBOX_ERROR',type(e).__name__)
            raise HTTPException(503,'Sandbox unavailable: '+str(e)[:120])
        store.update(task_id,step_index=index+1,state='complete' if index==1 else 'awaiting_next_step')
        store.log(task_id,'STEP_EXECUTED',f"Step {index+1}; exit={result['exit_code']}; timeout={result['timed_out']}; code_sha256={result['code_sha256']}; output_sha256={result['stdout_sha256']}")
        try: explanation=explain_output(task['goal'],step['name'],result)
        except Exception: explanation='AI explanation unavailable; verified execution evidence shown above.'
        return {'decision':'ALLOW','step':index+1,'result':result,
                'explanation':explanation,'next':'Revoke now to demonstrate dynamic permissions' if index==0 else 'Completed'}
    finally:lock.release()

@app.get('/api/audit/verify')
async def audit_verify(_:None=Depends(auth)):return {'integrity':store.audit_valid()}


CONTAINMENT_SCRIPTS={
    'network': "import socket\ns=socket.socket();s.settimeout(2)\ntry:\n s.connect(('1.1.1.1',443));print('UNEXPECTED: network reachable')\nexcept OSError as e: print('CONTAINED: outbound connection denied:',type(e).__name__)\nfinally:s.close()",
    'hostfiles': "from pathlib import Path\np=Path('/host/private_credentials.txt')\nprint('Host secret visible:',p.exists())\nassert not p.exists(), 'Host secret path unexpectedly visible'\nprint('CONTAINED: host path unavailable')",
    'readonly': "from pathlib import Path\ntry:\n Path('/malicious.txt').write_text('bad');print('UNEXPECTED: root filesystem writable')\nexcept OSError as e: print('CONTAINED: root filesystem is read-only:',type(e).__name__)",
    'timeout': "import time\nprint('Waiting...')\ntime.sleep(30)"
}
class ContainmentRequest(BaseModel):
    scenario:str
@app.post('/api/containment')
def containment(body:ContainmentRequest,_:None=Depends(auth)):
    if body.scenario not in CONTAINMENT_SCRIPTS:raise HTTPException(422,'Unknown containment scenario')
    if not lock.acquire(blocking=False):raise HTTPException(429,'Sandbox is currently busy')
    try:
        try:result=runner.execute(CONTAINMENT_SCRIPTS[body.scenario])
        except Exception as e:raise HTTPException(503,'Sandbox unavailable: '+str(e)[:120])
        store.log('CONTAINMENT', 'CONTAINMENT_TEST',f"{body.scenario}; exit={result['exit_code']}; timed_out={result['timed_out']}; sha256={result['stdout_sha256']}")
        return {'scenario':body.scenario,'result':result,'actual_execution':True}
    finally:lock.release()


# --- PUBLIC SHOWCASE (separate from the authenticated execution gateway) ---
# No AI inference, Docker access, shared SQLite writes, or administrative APIs.
# This environment is intentionally an ephemeral, synthetic-data demonstration.
public_demo_lock = threading.RLock()
public_demo_tasks = {}
public_demo_hits = {}
PUBLIC_MAX_TASKS = 200
PUBLIC_TTL = 20 * 60


def _public_limit(request: Request):
    # Simple in-process abuse guard. Use a reverse-proxy rate limiter for production.
    ip = request.client.host if request.client else 'unknown'
    now = time.monotonic()
    with public_demo_lock:
        hits = public_demo_hits.setdefault(ip, deque())
        while hits and hits[0] < now - 60:
            hits.popleft()
        if len(hits) >= 50:
            raise HTTPException(429, 'Public demo rate limit reached. Try again in a minute.')
        hits.append(now)
        if len(public_demo_hits) > 2000:
            public_demo_hits.clear()


def _public_clean():
    now = time.time()
    expired = [k for k, t in public_demo_tasks.items() if t['_created_ts'] + PUBLIC_TTL < now]
    for k in expired:
        del public_demo_tasks[k]
    if len(public_demo_tasks) >= PUBLIC_MAX_TASKS:
        oldest = min(public_demo_tasks, key=lambda k: public_demo_tasks[k]['_created_ts'])
        del public_demo_tasks[oldest]


def _public_view(t):
    return {k: v for k, v in t.items() if not k.startswith('_') and k not in ('events', 'goal')}


def _public_event(t, event, detail):
    t['events'].append({'event':event,'detail':detail,'timestamp':datetime.now(timezone.utc).isoformat()})


@app.get('/public', response_class=HTMLResponse)
@app.get('/', response_class=HTMLResponse)
async def public_homepage():
    return (BASE/'public_demo.html').read_text(encoding='utf-8')


@app.get('/api/public/status')
async def public_status():
    return {'status':'ok','mode':'fixture','public_demo':True,'sandbox_available':False}


@app.post('/api/public/tasks')
async def public_create(body: Goal, request: Request):
    _public_limit(request)
    from .inference import fixture_plan
    with public_demo_lock:
        _public_clean()
        now = datetime.now(timezone.utc)
        task = {'id':str(uuid.uuid4()),'created_at':now.isoformat(),
                'expires_at':(now+timedelta(seconds=PUBLIC_TTL)).isoformat(),
                'step_index':0,'max_steps':2,'revoked':0,'state':'ready',
                'steps':[{'name':s['name'],'reason':s['reason']} for s in fixture_plan(body.goal)],
                '_created_ts':time.time(),'events':[]}
        _public_event(task,'TASK_CREATED','Public demo task created using synthetic sample data')
        _public_event(task,'PLAN_READY','Two predefined steps; no AI inference or code execution')
        public_demo_tasks[task['id']]=task
        return {'task':_public_view(task),'inference_model':'PUBLIC FIXTURE (not AI)'}


@app.get('/api/public/tasks/{task_id}')
async def public_read(task_id:uuid.UUID, request:Request):
    _public_limit(request)
    with public_demo_lock:
        _public_clean()
        t=public_demo_tasks.get(str(task_id))
        if not t: raise HTTPException(404, 'Public demo task not found or expired')
        return {'task':_public_view(t),'events':list(t['events']),
                'audit_integrity':None,'note':'Ephemeral demo timeline; not signed audit evidence'}


@app.post('/api/public/tasks/{task_id}/revoke')
async def public_revoke(task_id:uuid.UUID, request:Request):
    _public_limit(request)
    with public_demo_lock:
        _public_clean()
        t=public_demo_tasks.get(str(task_id))
        if not t: raise HTTPException(404, 'Public demo task not found or expired')
        if not t['revoked']:
            t['revoked']=1;t['state']='revoked'
            _public_event(t,'PERMISSION_REVOKED','Public demo permission revoked; future steps denied')
        return {'status':'revoked','mode':'public_fixture'}


@app.post('/api/public/tasks/{task_id}/execute-next')
async def public_try_execution(task_id:uuid.UUID, request:Request):
    _public_limit(request)
    with public_demo_lock:
        _public_clean()
        t=public_demo_tasks.get(str(task_id))
        if not t: raise HTTPException(404, 'Public demo task not found or expired')
        why=('Permission revoked' if t['revoked'] else 'No sandbox configured in public fixture demo')
        _public_event(t,'POLICY_DENIED',why+'; no code executed')
        return {'decision':'BLOCK','reason':why,'executed':False,'simulation':True}


@app.get('/api/public/audit/verify')
async def public_audit_status():
    return {'integrity':None,'mode':'ephemeral_demo','message':'Public demo records are not signed audit logs'}


@app.post('/api/public/containment')
async def public_containment(request:Request):
    _public_limit(request)
    raise HTTPException(503, 'Public demo does not execute containment tests. Linux Docker is required.')

