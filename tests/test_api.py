import os
os.environ.setdefault('AB_DEMO_PASSWORD','unit-test-pass')
os.environ.setdefault('AB_AUDIT_KEY','unit-test-hmac')
os.environ.setdefault('LOCAL_FIXTURE_MODE','1')
from fastapi.testclient import TestClient
from agentboundary.server import app,store
from agentboundary.runner import Sandbox
import agentboundary.server as server
import base64

client=TestClient(app)
def headers():return {'Authorization':'Basic '+base64.b64encode(b'judge:unit-test-pass').decode(),'X-AgentBoundary-UI':'1'}

def test_health():assert client.get('/healthz').status_code==200

def test_unauth():assert client.get('/api/audit/verify').status_code==401

def test_no_custom_header():assert client.post('/api/tasks',headers={'Authorization':headers()['Authorization']},json={'goal':'analyze synthetic data'}).status_code==403

def test_plan_and_revoke(monkeypatch):
    r=client.post('/api/tasks',headers=headers(),json={'goal':'analyze synthetic sales report'});assert r.status_code==200,r.text
    tid=r.json()['task']['id']
    class Fake:
        def execute(self,code):return {'exit_code':0,'stdout':'ok','stderr':'','timed_out':False,'code_sha256':'a','stdout_sha256':'b','container':'mock','cleanup':'mock'}
    monkeypatch.setattr(server,'runner',Fake())
    x=client.post(f'/api/tasks/{tid}/execute-next',headers=headers());assert x.json()['decision']=='ALLOW'
    client.post(f'/api/tasks/{tid}/revoke',headers=headers())
    blocked=client.post(f'/api/tasks/{tid}/execute-next',headers=headers()).json()
    assert blocked['decision']=='BLOCK'

def test_containment_calls_runner(monkeypatch):
    class Fake:
        def execute(self,code):return {'exit_code':0,'stdout':'CONTAINED','stderr':'','timed_out':False,'code_sha256':'a','stdout_sha256':'b'}
    monkeypatch.setattr(server,'runner',Fake())
    x=client.post('/api/containment',headers=headers(),json={'scenario':'network'})
    assert x.status_code==200 and x.json()['actual_execution'] is True

def test_unknown_containment():assert client.post('/api/containment',headers=headers(),json={'scenario':'nonsense'}).status_code==422

def test_invalid_goal():assert client.post('/api/tasks',headers=headers(),json={'goal':'a'}).status_code==422
