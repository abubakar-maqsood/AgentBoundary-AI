"""Pure policy decision layer. No LLM or network access here."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import hashlib, hmac, json, secrets, sqlite3, threading, uuid

MAX_GOAL=650

def utcnow(): return datetime.now(timezone.utc)
def stamp(): return utcnow().isoformat()

def permit(task, step_index):
    if task['revoked']: return False, 'Task permission was revoked'
    if utcnow() >= datetime.fromisoformat(task['expires_at']): return False, 'Temporary permission expired'
    if step_index != task['step_index']: return False, 'Unexpected step index'
    if step_index >= len(task['steps']): return False, 'Task already finished'
    if step_index >= task['max_steps']: return False, 'Step count exceeds approved scope'
    return True,'Within task scope'

class Store:
    def __init__(self, path, audit_key):
        self.conn = sqlite3.connect(path,check_same_thread=False)
        self.conn.row_factory=sqlite3.Row
        self.conn.execute('PRAGMA journal_mode=WAL')
        self.conn.executescript('''
            CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY, goal TEXT NOT NULL, created_at TEXT NOT NULL, expires_at TEXT NOT NULL,
            revoked INTEGER DEFAULT 0, step_index INTEGER DEFAULT 0, max_steps INTEGER DEFAULT 2, state TEXT NOT NULL, steps TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT, task_id TEXT NOT NULL, timestamp TEXT NOT NULL,
            event TEXT NOT NULL, detail TEXT NOT NULL, previous_hash TEXT NOT NULL, digest TEXT NOT NULL);
        ''')
        self.conn.commit(); self.lock=threading.RLock();self.key=audit_key.encode()
    def log(self,task_id,event,detail):
        # Never record prompts containing API keys, generated code, or raw sandbox output.
        with self.lock:
            prev=self.conn.execute('SELECT digest FROM audit ORDER BY id DESC LIMIT 1').fetchone()
            parent=prev['digest'] if prev else 'GENESIS'
            date=stamp(); body=json.dumps([task_id,date,event,detail,parent],separators=(',',':'))
            digest=hmac.new(self.key,body.encode(),hashlib.sha256).hexdigest()
            self.conn.execute('INSERT INTO audit(task_id,timestamp,event,detail,previous_hash,digest) VALUES (?,?,?,?,?,?)',
                              (task_id,date,event,detail,parent,digest));self.conn.commit()
    def audit_valid(self):
        with self.lock:
            prev='GENESIS'
            for r in self.conn.execute('SELECT * FROM audit ORDER BY id'):
                body=json.dumps([r['task_id'],r['timestamp'],r['event'],r['detail'],r['previous_hash']],separators=(',',':'))
                good=hmac.new(self.key,body.encode(),hashlib.sha256).hexdigest()
                if not hmac.compare_digest(good,r['digest']) or prev!=r['previous_hash']:return False
                prev=r['digest']
        return True
    def add(self,goal,steps,minutes=20):
        with self.lock:
            ident=str(uuid.uuid4());now=utcnow(); deadline=(now+timedelta(minutes=minutes)).isoformat()
            self.conn.execute('INSERT INTO tasks(id,goal,created_at,expires_at,state,steps) VALUES(?,?,?,?,?,?)',
                              (ident,goal,now.isoformat(),deadline,'ready',json.dumps(steps)))
            self.conn.commit();self.log(ident,'TASK_CREATED','Two-step sandbox workflow authorized')
            return self.get(ident)
    def get(self,ident):
        with self.lock:
            row=self.conn.execute('SELECT * FROM tasks WHERE id=?',(ident,)).fetchone()
        if not row:return None
        t=dict(row);t['steps']=json.loads(t['steps']);return t
    def update(self,ident,**changes):
        allowed={'revoked','step_index','state'}
        assert set(changes)<=allowed
        with self.lock:
            for k,v in changes.items():self.conn.execute(f'UPDATE tasks SET {k}=? WHERE id=?',(v,ident))
            self.conn.commit()
    def events(self,ident):
        with self.lock:
            rows=self.conn.execute('SELECT timestamp,event,detail,digest FROM audit WHERE task_id=? ORDER BY id',(ident,)).fetchall()
        return [dict(r) for r in rows]
    def close(self):self.conn.close()
