## Public showcase + protected admin 

- `/` and `/public`: **No-login public demo** with predefined synthetic steps, permission revocation, and ephemeral per-task event timeline.
- `/admin`: **Password-protected original dashboard**, using `AB_DEMO_USER` and `AB_DEMO_PASSWORD`.
- `/api/public/*`: restricted fixture-only demo operations. **No AI calls, Docker execution, secrets, persistent audit DB writes, or filesystem access**.
- `/api/*`: original authenticated routes; keep credentials private.

The public demo does not constitute Vultr deployment or real sandbox containment. The public event timeline is not a cryptographically signed audit log.

Public demo uses in-memory tasks, lost on restart. Keep `AB_DEMO_PASSWORD` and `AB_AUDIT_KEY` configured on Render; avoid exposing them. See `PUBLIC_DEMO_DEPLOY.md`.

---

> **Free-hosted showcase notice:** The `render.yaml` configuration runs `LOCAL_FIXTURE_MODE=1` with sample planning only. It does not run live Vultr AI or a real Docker sandbox; see [START_HERE_UPLOAD.md](START_HERE_UPLOAD.md).

# AgentBoundary AI — Vultr Agent Rush Edition

**Challenge:** Vultr: Agent Rush Hackathon → **Blast Radius Zero (Challenge 1)**.

An AI coding agent that takes a plain-language synthetic-data task, plans two executable Python steps via **Vultr Serverless Inference**, sends each step into a **fresh disposable rootless Docker sandbox on a Vultr Cloud Compute VM**, verifies real execution receipts, and supports **immediate permission revocation between steps**.

> Status: Tested Python engine and HTTP API locally (27 automated tests). **Not deployed or live-tested on a Vultr VM from this environment.** Container execution requires rootless Docker and should be verified on your own VM. Do not advertise this as production-grade anti-malware or comprehensive endpoint protection.

## Why it exists

AI agents are useful when they can execute code, but an agent should not gain unlimited authority. AgentBoundary separates **proposal (LLM)** from **permission decision (deterministic policy)** and **execution (sandbox)**.

## Product features

1. **Real Vultr-powered agent**: chat completions plan two independent Python programs; a second inference call explains the executed output without tools.
2. **Two-step permission checkpoints**: only one code step is authorized at a time. After step one you can revoke or let the second proceed. The step-two policy is checked again immediately before execution.
3. **Disposable sandbox**: Docker CLI starts a new container with no network, non-root identity, read-only root filesystem, no capabilities, no new privileges, no IPC, PID/CPU/memory/time limits, and a read-only script mount. Each container is force removed afterward.
4. **Isolation demonstrations**: actual tests for network access, host path visibility, root filesystem writes, and time limits.
5. **Evidence receipts**: hash of generated code, hash of output, exit code, stdout/stderr, timeout status, and task decisions.
6. **Audit chain**: HMAC-linked records detect edits in the stored chain. This **does not** prevent deletion of the entire database or compromise of the local key.
7. **Public demo UI**: web interface for plans, step execution, revocation, containment, and audit history, protected by Basic auth under HTTPS.

## Architecture

```
public browser → HTTPS Caddy → FastAPI (Vultr VM)
                                  ├─ Vultr Serverless Inference (plans/explanations)
                                  ├─ task policy + SQLite audit
                                  └─ rootless Docker daemon
                                      └─ fresh python:3.12-alpine container
                                         ├─ no network
                                         ├─ no host secrets
                                         ├─ limited RAM/CPU/time
                                         └─ actual Python output
```

**Security boundaries:** Generated code is never evaluated with Python `exec()` in the server process. The sandbox can see only its generated script. The API key stays in the orchestration service. The service refuses rootful Docker. The Docker daemon and its control socket are still sensitive; protect them and consider stronger kernel isolation (gVisor/microVMs) for future commercial deployments. A compromised host/rootless daemon or kernel vulnerability can still break containment.

## Local testing without Vultr account (UI/inference fixture only)

Python 3.11+:

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export AB_DEMO_PASSWORD='a-local-passphrase-at-least-16-chars'
export AB_AUDIT_KEY='a-different-local-test-key-at-least-32-chars'
export LOCAL_FIXTURE_MODE=1
python run.py
```

Open http://127.0.0.1:8765. Username `judge`, password from `AB_DEMO_PASSWORD`.

**Fixture mode** generates two canned scripts. It is **not live AI**, and the sandbox still requires rootless Docker for execution. It must be **disabled in the hackathon production deployment**.

## Automated tests

```bash
python -m pytest -q
```

Expected in our test environment: **27 passed**. These tests use a mock sandbox for API checks and static checking of Docker flags; they do **not** prove containment under a real Linux kernel.

## Actual Vultr deployment

Follow [docs/DEPLOY_VULTR_ROMAN_URDU.md](docs/DEPLOY_VULTR_ROMAN_URDU.md) and [docs/SECURITY_AND_TESTS.md](docs/SECURITY_AND_TESTS.md). A domain name, API key, credits, Linux server, and rootless Docker setup require action by the owner of the Vultr account.

## What goes in your hackathon submission

- Public HTTPS URL running the app from a **Vultr Cloud Compute VM**
- **Vultr Serverless Inference** key (server-side only) + model used
- GitHub repository with this README and deployed architecture
- Recorded video showing **real sandbox execution + a containment moment + permission revocation**
- Slides, cover art, short description, team information, and LabLab submission

See [docs/HACKATHON_SUBMISSION.md](docs/HACKATHON_SUBMISSION.md).

## Limitations (be explicit with judges)

- Protects **this demo agent workflow**, not installed Cursor, Codex, browsers or Windows.
- Does not inspect arbitrary user files, personal passwords or customer databases.
- Dynamic revocation works **between steps**; it cannot interrupt an already running container. Runtime timeout limits single-step execution.
- HMAC-linked audit receipts detect edits when the key and full database remain trustworthy; they are not remote attestations or digitally signed evidence.
- Sandbox hardening depends on correct Linux rootless Docker and kernel settings. Full penetration testing is pending.
- No external user accounts/teams, billing system, or persistent workspaces.
- No real deploy or live inference call has been verified in this environment.

## License

MIT, see `LICENSE`. Review all dependencies' licenses before submission.
