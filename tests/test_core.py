import os, sqlite3, tempfile, pytest
from datetime import timedelta
from agentboundary.core import Store,permit,utcnow
from agentboundary.inference import fixture_plan,parse_plan
from agentboundary.runner import docker_arguments
from pathlib import Path

@pytest.fixture
def store(tmp_path):
    s=Store(str(tmp_path/'events.db'),'test-key');yield s;s.close()

def task(s):return s.add('analyze example data',fixture_plan('x'))

def test_create(store):
    t=task(store);assert t['step_index']==0 and len(t['steps'])==2

def test_allow_first(store):
    t=task(store);assert permit(t,0)[0]

def test_wrong_step(store):
    t=task(store);assert not permit(t,1)[0]

def test_revoke(store):
    t=task(store);store.update(t['id'],revoked=1);assert not permit(store.get(t['id']),0)[0]

def test_expired(store):
    t=task(store);t['expires_at']=(utcnow()-timedelta(seconds=1)).isoformat();assert not permit(t,0)[0]

def test_step_limit(store):
    t=task(store);t['step_index']=2;assert not permit(t,2)[0]

def test_audit_valid(store):
    task(store);assert store.audit_valid()

def test_audit_tamper(store):
    task(store);store.conn.execute("UPDATE audit SET event='HIDDEN' WHERE id=1");store.conn.commit();assert not store.audit_valid()

def test_audit_chain(store):
    t=task(store);store.log(t['id'],'TEST','done');assert store.audit_valid()

def test_fixture_steps():assert len(fixture_plan('anything'))==2

def test_parse_json():
    import json
    assert len(parse_plan(json.dumps({'steps':fixture_plan('x')})))==2

def test_parse_markdown():
    import json
    assert len(parse_plan('```json\n'+json.dumps({'steps':fixture_plan('x')})+'\n```'))==2

def test_reject_one_step():
    with pytest.raises(ValueError):parse_plan('{"steps":[]}')

def test_reject_oversize():
    import json
    x=fixture_plan('x');x[0]['code']='a'*1501
    with pytest.raises(ValueError):parse_plan(json.dumps({'steps':x}))

def test_sandbox_no_network(tmp_path):
    args=docker_arguments(tmp_path/'task.py','demo-safe')
    assert args[args.index('--network')+1]=='none'

def test_sandbox_no_root(tmp_path):
    args=docker_arguments(tmp_path/'task.py','demo-safe')
    assert args[args.index('--user')+1]=='65534:65534'

def test_sandbox_readonly(tmp_path):
    args=docker_arguments(tmp_path/'task.py','demo-safe')
    assert '--read-only' in args and '--cap-drop' in args

def test_sandbox_memory(tmp_path):
    args=docker_arguments(tmp_path/'task.py','demo-safe')
    assert '128m' in args and '--pids-limit' in args

def test_sandbox_no_privileges(tmp_path):
    args=docker_arguments(tmp_path/'task.py','demo-safe')
    assert 'no-new-privileges' in args

def test_sandbox_no_secret_env(tmp_path):
    args=docker_arguments(tmp_path/'task.py','demo-safe')
    assert '--env' not in args and '-e' not in args
