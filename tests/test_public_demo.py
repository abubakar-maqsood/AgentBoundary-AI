import os
os.environ.setdefault('AB_DEMO_PASSWORD','unit-test-pass')
os.environ.setdefault('AB_AUDIT_KEY','unit-test-hmac')
os.environ.setdefault('LOCAL_FIXTURE_MODE','1')
from fastapi.testclient import TestClient
from agentboundary.server import app
import agentboundary.server as server

client=TestClient(app)

def test_open_homepage_and_protected_admin():
    r=client.get('/')
    assert r.status_code==200 and 'PUBLIC DEMO · NO LOGIN' in r.text
    assert client.get('/admin').status_code==401

def test_public_plan_revoke_and_events():
    r=client.post('/api/public/tasks',json={'goal':'Calculate a synthetic dataset example'})
    assert r.status_code==200, r.text
    d=r.json(); assert 'PUBLIC FIXTURE' in d['inference_model']
    tid=d['task']['id']
    before=client.get('/api/public/tasks/'+tid)
    assert before.status_code==200 and before.json()['task']['revoked']==0
    rev=client.post('/api/public/tasks/'+tid+'/revoke')
    assert rev.status_code==200 and rev.json()['status']=='revoked'
    after=client.get('/api/public/tasks/'+tid).json()
    assert after['task']['revoked']==1
    assert any(e['event']=='PERMISSION_REVOKED' for e in after['events'])
    assert after['audit_integrity'] is None

def test_public_never_executes_code(monkeypatch):
    r=client.post('/api/public/tasks',json={'goal':'Analyze synthetic data with sample orders'})
    tid=r.json()['task']['id']
    class Trap:
        def execute(self, _):
            raise AssertionError('Sandbox must never be invoked by public API')
    monkeypatch.setattr(server,'runner',Trap())
    check=client.post('/api/public/tasks/'+tid+'/execute-next')
    assert check.status_code==200
    assert check.json()['decision']=='BLOCK' and check.json()['executed'] is False
    assert client.post('/api/public/containment').status_code==503

def test_admin_apis_still_require_login():
    assert client.post('/api/tasks',json={'goal':'Analyze synthetic data now'}).status_code==401
    assert client.get('/api/audit/verify').status_code==401
    assert client.post('/api/containment',json={'scenario':'network'}).status_code==401

def test_public_only_accepts_valid_goals_and_ids():
    assert client.post('/api/public/tasks',json={'goal':'short'}).status_code==422
    assert client.get('/api/public/tasks/not-a-uuid').status_code==422
