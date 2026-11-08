# AgentBoundary AI — GitHub + Render Free Demo

Created by **The Explorers**.

## What this package can show

- The animated dashboard and project explanations
- **Fixture-mode** two-step planning (`LOCAL FIXTURE — NOT AI`)
- Task permission revocation and denial of a later step
- Task/audit event views (as far as the ephemeral database remains available)

**What it cannot prove on a free Render service:** Vultr AI inference, real Docker sandbox execution, secure containment, or compliance with the Vultr Agent Rush Challenge 1 hosting requirement. Do not call those capabilities live unless separately verified on Vultr with the required sandbox. `Execute next step` and containment actions can return **Sandbox unavailable** on Render.

## Step A — GitHub web upload (no terminal needed)

1. Go to https://github.com/new and create a **Public** repository named `AgentBoundary-AI`. Do not select *Initialize with README* if you plan to upload this full set.
2. Unzip this file on your computer.
3. On the repository page select **Add file → Upload files**.
4. Upload **the contents of this extracted folder**, preserving the directories `agentboundary/`, `tests/`, `docs/`, `deploy/` and `scripts/` and files in the root. GitHub drag-and-drop of folders works in some browsers; if it flattens folders, use GitHub Desktop instead.
5. Commit. Check that `agentboundary/server.py`, `agentboundary/ui.html`, `requirements.txt`, `render.yaml` and `README.md` are reachable in the repository.

**Never upload** `.env`, `.venv`, API keys, passwords, SQLite databases or real customer data. This ZIP excludes them.

## Step B — Render.com free web service

1. Log into https://dashboard.render.com/ and connect GitHub.
2. Select **New → Web Service** and the `AgentBoundary-AI` repository.
3. Select the **Free** instance type if available for your account.
4. Set **Build command**: `pip install -r requirements.txt`
5. Set **Start command**: `uvicorn agentboundary.server:app --host 0.0.0.0 --port $PORT`
6. Add environment variables:
   - `LOCAL_FIXTURE_MODE` = `1`
   - `AB_DEMO_USER` = `judge`
   - `AB_DEMO_PASSWORD` = your own **unique 16+ character** password
   - `AB_AUDIT_KEY` = unique random 32+ character string (store privately; never publish)
7. Deploy. The `.onrender.com` URL becomes available when build/start succeeds.
8. Open `/healthz` to verify app is running, then open `/` and sign in using the username/password.

**Note:** `render.yaml` is also included if you use Render's Blueprint deployment. In either path, check the environment settings before making the site public. Do not assume a successful web deployment proves real agent execution.

## Step C — Demo walkthrough

1. In the dashboard, enter a sample calculation and click **Generate with Vultr AI** (the mode label correctly says *LOCAL FIXTURE — NOT AI*).
2. Observe the two-step sample plan and task ID.
3. Click **Revoke permission** before execution.
4. Click **Execute next step**, which should show a policy denial instead of attempting Docker execution.
5. Inspect **Evidence and audit**; if integrity is invalid, stop making audit-integrity claims and investigate; Render's ephemeral filesystem can also reset logs when redeploying.

## Test locally

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

## Honest event submission note

The event's *Blast Radius Zero* track requires execution inside a Vultr-hosted isolated sandbox and Vultr Serverless Inference; Render fixture mode is a **backup public showcase**, not an eligible substitute for those required integrations. Ask the organizers whether a noncompliant prototype can still be submitted and whether participation certificates are offered.
