# Public access, protected admin — deployment guide

1. Upload all modified files to the existing GitHub repository, preserving paths, including new `agentboundary/public_demo.html`. Do not upload `.env` or secrets.
2. Render → your service → Manual Deploy → Deploy latest commit (or wait for auto-deploy). Keep the existing Free plan and start command.
3. Environment: `LOCAL_FIXTURE_MODE=1`, `AB_DEMO_USER`, `AB_DEMO_PASSWORD`, and stable `AB_AUDIT_KEY`. Do not share secrets.
4. Open the public URL in an incognito window. `/` must show PUBLIC DEMO · NO LOGIN, and generating a fixture task and revocation should work without authentication.
5. Open `/admin` in an incognito window. Basic Auth should ask for username/password. The original `/api/tasks` without authentication must return 401.
6. Public demo does not run code, Docker, AI inference or the signed audit database. Do not claim that it does. No private data should be entered.
7. Inspect the network and server logs if a request fails; missing sandbox is expected for the original admin execute API.

Security note: This is a limited public demonstration, not a production multi-tenant authentication system. Its rate guard is per-process; deploy behind provider/WAF-level rate limiting for public traffic.
