"""Run on the Vultr VM, under the same account used by the application."""
import os,shutil,subprocess,sys

def check(name,ok,info=''):
    print(('PASS' if ok else 'FAIL')+'  '+name+(' — '+info if info else ''))
    return ok

ok=True
ok &= check('Python 3.11+',sys.version_info>=(3,11),sys.version.split()[0])
ok &= check('AB_DEMO_PASSWORD configured',len(os.environ.get('AB_DEMO_PASSWORD',''))>=16)
ok &= check('AB_AUDIT_KEY configured',len(os.environ.get('AB_AUDIT_KEY',''))>=32)
ok &= check('Vultr Inference key configured',len(os.environ.get('VULTR_INFERENCE_API_KEY',''))>10)
ok &= check('LIVE inference mode',os.environ.get('LOCAL_FIXTURE_MODE')!='1')
exists=bool(shutil.which('docker'));ok &= check('Docker CLI present',exists)
if exists:
    try:
        r=subprocess.run(['docker','info','--format','{{json .SecurityOptions}}'],capture_output=True,text=True,timeout=10)
        ok &= check('Rootless Docker available',r.returncode==0 and 'rootless' in r.stdout.lower(),r.stdout.strip()[:160])
        img=subprocess.run(['docker','image','inspect','python:3.12-alpine'],capture_output=True,text=True,timeout=10)
        ok &= check('Sandbox image present',img.returncode==0)
    except Exception as e:ok &= check('Docker preflight',False,str(e))
print('\nOverall:', 'READY FOR LIVE TESTS' if ok else 'NOT READY: fix the failures above')
sys.exit(0 if ok else 1)
