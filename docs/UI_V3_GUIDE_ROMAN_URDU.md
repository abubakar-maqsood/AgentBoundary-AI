# AgentBoundary AI — The Explorers UI v3

## Kya badla hai?
- Pehle se existing dark navy / blue / teal professional theme preserve ki.
- **How It Works**: Define task → Generate plan → Check permissions → Sandbox execute → Review evidence.
- **Security Controls**: Task-scope, re-check and revoke, sandbox, no-network mode, resource limits, audit events.
- **Operator Guide**: Har dashboard action ka purpose, mode difference, aur FAQ.
- **Created by The Explorers** branding retained.

## Cursor mein updated dashboard lagana
1. Current server terminal mein Ctrl+C press karo.
2. ZIP extract karo.
3. Existing `D:\Hackathons\AgentBoundary_AgentRush_Vultr\agentboundary\ui.html` ko backup bana ke is ZIP wali `agentboundary/ui.html` se replace karo.
4. Existing database, `.env`, audit key, `.venv`, aur credentials copy/replace **mat** karna.
5. Cursor PowerShell (project root) mein run karo: `.\.venv\Scripts\python.exe run.py`
6. Browser `http://127.0.0.1:8765` open karo, zaroorat ho toh Ctrl+Shift+R.
7. Tests: `.\.venv\Scripts\python.exe -m pytest -q`.

## Functioning limitations
- Windows pe **LOCAL FIXTURE** ka matlab sample AI plan hai. Real Vultr inference ki guarantee nahi.
- Real containment Linux host par configured rootless Docker ke saath test karna hai.
- Dashboard aur gateway sirf un actions ko protect karte hain jo is software se pass hon.
- Pehle ka `Audit chain INVALID` issue automatically is UI update se resolve nahi hoga. Usko separately diagnose karna hai.
