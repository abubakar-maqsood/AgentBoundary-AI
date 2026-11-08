# AgentBoundary UI v4 — The Explorers

Changes to `agentboundary/ui.html` only. No backend security rules or APIs were modified.

- Refined dark navy/teal, subtle shield motion, hover and focus states, reduced-motion support.
- Honest Local Fixture vs Live Vultr Inference state (read from `/healthz`, NOT a mode switch).
- Four-stage interactive task progress rail with execution status.
- Busy/loading button states, user-facing notifications, confirmation before permission revocation.
- Accessible scenario guidance, more readable results, responsive layouts.
- Updated workflow, containment and security descriptions; preserves The Explorers credit.

## Install in existing Cursor project
1. Stop running server (Ctrl+C).
2. Back up existing `agentboundary/ui.html`.
3. Replace only `agentboundary/ui.html` from this zip.
4. Keep `.env`, `.venv`, audit database and keys unchanged.
5. Start with `.\.venv\Scripts\python.exe run.py` in the same terminal with configured AB_DEMO_PASSWORD and AB_AUDIT_KEY.
6. Reload browser at http://127.0.0.1:8765 (Ctrl+Shift+R).
7. Run `.\.venv\Scripts\python.exe -m pytest -q`.

## Modes
- LOCAL_FIXTURE_MODE=1: plan is predefined; NOT AI.
- LOCAL_FIXTURE_MODE=0: live planning requires configured Vultr inference credentials/model.
- Neither mode makes real Docker execution possible on Windows without a configured Linux sandbox runner.
- No UI switch can enable live mode independently of backend configuration.

## Security caveats
- This remains a research prototype; only its mediated agent workflow is in scope.
- Old audit-chain INVALID state must be investigated separately; this UI does not repair it.
- Do not submit real passwords, banking info or private customer datasets.
