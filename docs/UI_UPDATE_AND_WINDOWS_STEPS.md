# AgentBoundary UI refresh — Windows / Cursor steps

This update changes only `agentboundary/ui.html`. Backend endpoints and permission logic remain unchanged.

## Install the updated dashboard

1. Stop the running server in Cursor with `Ctrl+C`.
2. Safest path: extract the updated ZIP into a **new folder**, so your existing local database and `.env` are not overwritten. Or copy only `agentboundary/ui.html` from this package over the same file in your existing project.
3. Keep using the existing Python virtual environment and environment variables in your original project when replacing only the HTML file.
4. Start the server from your project folder:
   ```powershell
   .\.venv\Scripts\python.exe run.py
   ```
5. Open `http://127.0.0.1:8765` and sign in with the locally configured dashboard username/password.
6. Refresh using `Ctrl+Shift+R` if the old interface appears.

## What changed

- Consistent dark navy/blue dashboard theme with restrained teal highlights.
- Sidebar navigation and overview metric cards.
- Cleaner task planner and active-task progression.
- Separate containment testing and evidence sections.
- Responsive phone/tablet layout, keyboard focus styles, and reduced-motion support.
- Brand text: **Created by The Explorers** in the sidebar and footer.

## Functionality checks

- [ ] Log in and check the fixture/live status badge.
- [ ] Create a two-step plan. In local fixture mode it is not live AI inference.
- [ ] Confirm the two steps appear and permission controls update.
- [ ] On a Vultr Linux VM with rootless Docker, test sandbox execution and containment.
- [ ] Refresh audit evidence and investigate any `Audit chain INVALID` result before production.

**Do not upload actual passwords, credentials, customer records, or private files.** The Windows dashboard does not automatically protect local applications. Sandbox execution requires configured Linux infrastructure.
