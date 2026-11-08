"""Real execution in disposable, no-network Docker containers.
Never invoke generated code in the host interpreter.
"""
import hashlib, os, shutil, subprocess, tempfile, uuid
from pathlib import Path

IMAGE='python:3.12-alpine'

def docker_arguments(code_path, name):
    # Explicit argv: no shell interpolation; all job content mounted read-only.
    return ['docker','run','--rm','--name',name,'--network','none','--read-only',
      '--cpus','0.50','--memory','128m','--memory-swap','128m','--pids-limit','64',
      '--ipc','none','--cap-drop','ALL','--security-opt','no-new-privileges','--user','65534:65534',
      '--tmpfs','/tmp:rw,nosuid,nodev,noexec,size=16m',
      '--mount',f'type=bind,src={code_path.parent},dst=/job,readonly',
      '--workdir','/job','--entrypoint','python',IMAGE,'-I','-B','/job/task.py']

class Sandbox:
    def __init__(self, timeout=12):self.timeout=timeout
    def execute(self,code):
        if os.environ.get('DISABLE_EXECUTION')=='1':raise RuntimeError('Execution intentionally disabled')
        if not shutil.which('docker'):raise RuntimeError('Docker unavailable: cannot execute; never falling back to host')
        info=subprocess.run(['docker','info','--format','{{json .SecurityOptions}}'],capture_output=True,text=True,timeout=8,check=False)
        if info.returncode!=0 or 'rootless' not in info.stdout.lower():
            raise RuntimeError('Rootless Docker is required; refusing unsafe rootful Docker execution')
        name='ab-'+uuid.uuid4().hex[:16]
        with tempfile.TemporaryDirectory(prefix='ab-job-') as temp:
            path=Path(temp)/'task.py';path.write_text(code,encoding='utf-8');path.chmod(0o644);Path(temp).chmod(0o755)
            cmd=docker_arguments(path,name)
            try:
                run=subprocess.run(cmd,capture_output=True,text=True,timeout=self.timeout,check=False)
                return {'exit_code':run.returncode,'stdout':run.stdout[:3500],
                        'stderr':run.stderr[:2000],'timed_out':False,
                        'code_sha256':hashlib.sha256(code.encode()).hexdigest(),
                        'stdout_sha256':hashlib.sha256(run.stdout.encode()).hexdigest(),
                        'container':name,'cleanup':'--rm and forced cleanup'}
            except subprocess.TimeoutExpired:
                return {'exit_code':124,'stdout':'','stderr':'Execution time limit exceeded',
                        'timed_out':True,'code_sha256':hashlib.sha256(code.encode()).hexdigest(),
                        'stdout_sha256':hashlib.sha256(b'').hexdigest(),
                        'container':name,'cleanup':'forced cleanup'}
            finally:
                # Docker CLI can be killed on timeout; clean container separately.
                subprocess.run(['docker','rm','-f',name],capture_output=True,timeout=8,check=False)
