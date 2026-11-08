# Submission kit — copy, customize and verify

## Challenge
**Challenge 1: Blast Radius Zero**, Vultr: Agent Rush Hackathon, November 3–8, 2026.

## Team
The Explorers

## Project title
AgentBoundary AI — Task-Scoped Sandboxed Agents

## Short description
AgentBoundary AI runs real AI-generated Python tasks in disposable Vultr sandboxes while enforcing revocable, task-scoped permissions and returning verifiable execution evidence.

## Long description (draft)
Autonomous agents are useful when they execute work, but a single blanket authorization may remain valid long after the user's intent changes. AgentBoundary AI introduces a security gateway between a Vultr-powered AI planner and isolated execution. Users request an analysis task, Vultr Serverless Inference produces two executable Python steps, and an independent policy checks permission before each step. Each script runs in a disposable rootless Docker container on a Vultr VM with no network, no injected secrets, a read-only root filesystem, and CPU, memory and time limits. The dashboard displays real stdout, exit codes, output hashes, containment tests, and a tamper-evident audit chain. Users can revoke task permission between steps, demonstrating that yesterday's approval cannot automatically authorize the next action. The product targets developers and companies that want real agent productivity without granting persistent blanket permissions. This version is a hackathon prototype, not universal computer or agent protection.

## Technology tags
Vultr Cloud Compute; Vultr Serverless Inference; Python; FastAPI; Docker; AI Agents; Cybersecurity; Sandbox; SQLite

## GitHub README must show
- Vultr VM and deployment architecture
- Vultr Serverless Inference usage, model ID and key handling
- Container isolation and disposable run configuration
- Setup and local tests
- Real project demo URL and screenshots
- Threat model, limitations, containment moment

## Demo video: suggested 3–4 minutes

**0:00–0:25 — Problem:** AI agents need execution permissions; blanket permissions can outlive the task.

**0:25–0:55 — Architecture:** Browser → Vultr VM FastAPI → Vultr Serverless Inference → independent policy → rootless Docker sandbox.

**0:55–1:35 — Real work:** Live public page; generate two-step sample-data task; execute step one and show numeric stdout, exit code and hashes.

**1:35–2:10 — Dynamic permission:** Revoke task, attempt second step, show BLOCK and audit event. Explain that action 1 was authorized and action 2 was not.

**2:10–2:45 — Containment:** Run real network/write/timeout tests; display actual error/output and no remaining container.

**2:45–3:20 — Business value and limitations:** API keys stay server-side, no host files mounted, sandbox cleanup; explain scope and roadmap.

**3:20–3:50 — Conclusion:** Reproducible Github, deployment proof, measurable comparative study future work.

Do not edit the footage to suggest a simulated or failed test succeeded; show actual results.

## Suggested pitch slides (8)
1. Problem and threat model
2. Why sandbox alone isn't enough (authorizations change)
3. AgentBoundary solution
4. System architecture on Vultr
5. Stepwise permit/revoke execution
6. Real containment evidence
7. Business value and differentiator
8. Limits, metrics, next iteration

## Final checks

- [ ] Confirm contest track, team, rules and originality/MIT license eligibility
- [ ] Connect live Vultr inference, deploy real VM backend, verify public HTTPS app
- [ ] Run real sandbox tasks and containment tests
- [ ] GitHub public repository and correct README
- [ ] Upload cover image, slide deck and recorded demo
- [ ] Fill LabLab project form, submit before deadline, confirm submission receipt
