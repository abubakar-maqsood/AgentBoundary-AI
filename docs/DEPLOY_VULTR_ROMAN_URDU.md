# AgentBoundary: Vultr par deployment — Roman Urdu guide

**Pehle samjho:** Code ready hai, lekin account create, credit claim, API key, VM, domain, DNS, aur LabLab submission **aapko apne account mein karna hoga**. Kisi ko real API key/password chat ya GitHub par mat bhejna.

## A. Pehle aapki checklist

1. LabLab par enrolled team `The Explorers` verify karo. Discord join kar lo.
2. https://lablab.build/ai-hackathons/vultr-hackathon par `$200` Vultr credit claim process follow karo. Billing mein remaining credit check karo.
3. Vultr account banao, email verify karo.
4. **Serverless Inference** activate karo aur secret API key generate karo (Vultr dashboard mein). Is key ko sirf VM par `.env` mein rakho.
5. Domain/subdomain choose karo, example `agentboundary.yourdomain.com`. Public HTTPS URL ke liye DNS A record VM IP par point karo.
6. Public GitHub repository banao. Sirf source upload karo; `.env`, private database, generated files aur credentials upload MAT karna.

## B. Vultr VM banao

Vultr Console → Products → Cloud Compute → Deploy. Ubuntu 24.04 LTS, public IPv4; **minimum 2 vCPU and 4GB RAM suggested** for demo, not a verified requirement. SSH key login choose karo. Pricing dashboard par verify karo. Cloud firewall mein port 22 (apni IP), 80, 443 allow karo. Port 8765 ko internet par expose mat karo.

Apne Windows PC se PowerShell open kar ke:

```powershell
ssh YOUR_LINUX_USER@YOUR_VM_IP
```

VM par:

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-venv python3-pip git uidmap dbus-user-session curl
```

## C. Rootless Docker install karo (important)

**Rootful Docker socket se application ko host root access ka risk hota hai.** Hamara runner rootless Docker detect na ho to execute karne se inkar karta hai. Official instructions check: https://docs.docker.com/engine/security/rootless/ .

Install Docker Engine binaries from official Docker documentation first (Ubuntu apt repository; follow https://docs.docker.com/engine/install/ubuntu/). Phir dedicated non-root account par rootless setup:

```bash
# As your NON-ROOT account (not sudo)
dockerd-rootless-setuptool.sh install
systemctl --user enable --now docker
sudo loginctl enable-linger "$USER"
export DOCKER_HOST="unix:///run/user/$(id -u)/docker.sock"
docker info --format '{{json .SecurityOptions}}'
```

Output mein `rootless` hona chahiye. Agar error aaye to setup issue solve karo; `sudo docker` ya rootful daemon ko shortcut ke taur par use na karo.

Then:

```bash
docker pull python:3.12-alpine
docker run --rm --network none python:3.12-alpine python -c 'print("sandbox image ready")'
```

Note: agar `--cpus` aur memory limits VM par fail hon, rootless Docker ke cgroup v2 and systemd requirements verify karo. Unverified limits ke saath public demo mat chalao.

## D. Application install karo

GitHub par project upload karne ke baad (recommended) VM par:

```bash
cd ~
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git agentboundary-agent-rush
cd agentboundary-agent-rush
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
chmod 600 .env
nano .env
```

`.env` mein:

- `AB_DEMO_PASSWORD` strong unique random password (16+ chars)
- `AB_AUDIT_KEY` **different** 32+ character random secret
- `VULTR_INFERENCE_API_KEY` actual Vultr key
- `VULTR_INFERENCE_MODEL` chosen available model (current example `deepseek-v4.1-flash-1017`)
- `LOCAL_FIXTURE_MODE=0` (REQUIRED FOR FINAL DEMO)
- `AB_PUBLIC_ORIGIN=https://YOUR_DOMAIN`

Secrets locally generate:

```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(40))'
```

Command twice run karo; passwords alag rakho.

Load env in this shell for preflight:

```bash
set -a
. ./.env
set +a
export DOCKER_HOST="unix:///run/user/$(id -u)/docker.sock"
python scripts/preflight.py
python -m pytest -q
python run.py
```

Browser par abhi URL local hai (127.0.0.1). Public access ke liye reverse proxy setup karo.

## E. Systemd background service

`deploy/agentboundary.service` copy karo. Us mein `YOUR_LINUX_USER` aur `YOUR_UID` replace karo (`id -u`). `ExecStart` path aur project directory verify karo.

```bash
sudo cp deploy/agentboundary.service /etc/systemd/system/agentboundary.service
sudo systemctl daemon-reload
sudo systemctl enable --now agentboundary
sudo systemctl status agentboundary --no-pager
```

Systemd EnvironmentFile `.env` read karta hai. Service user ko Docker rootless socket accessible hona chahiye. If not, check user service + DOCKER_HOST. App listens **127.0.0.1:8765** only.

## F. HTTPS domain (Caddy)

Domain/subdomain DNS A record ko VM IP par point karo. Install Caddy from official Ubuntu docs: https://caddyserver.com/docs/install . Then `deploy/Caddyfile` mein `YOUR_DOMAIN` replace karo.

```bash
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile
sudo caddy validate --config /etc/caddy/Caddyfile
sudo systemctl reload caddy
```

Now visit `https://YOUR_DOMAIN`. HTTP Basic login: user `judge`, password aapka set kiya hua. Judges ke liye alag restricted demo credential banana future improvement hai; filhal shared password compromise se koi demo tasks modify kar sakta hai, so rotate after judging. Domain/HTTPS ke baghair live password transmit mat karna.

## G. Live tests on Vultr

1. `/healthz` should return `{mode: "vultr"}`. If `fixture`, your demo is NOT eligible as a live AI integration.
2. Dashboard mein synthetic CSV task generate karo. Vultr model name show ho.
3. Execute step 1: real stdout, exit code and hash returned by a fresh Docker container.
4. **Revoke permission** click karo. Then **Execute next step** press karo: actual `BLOCK` decision + audit entry.
5. Containment tab mein Network, Read-only FS, Host-file visibility, Timeout scenarios test karo. Expected `CONTAINED` outputs / timeout status.
6. Audit integrity verify karo. Inspect `docker ps -a` for leftovers.
7. Re-plan a task and run both steps successfully, then show legitimate-task completion.
8. Record a 3–4 minute screen capture of actual public URL and VM overview (API keys hidden!).

## H. GitHub and final submission

- GitHub repository `Public`, add MIT LICENSE, setup docs, deployment architecture, `tests`.
- Replace README placeholders, add screenshots and your real deployment URL.
- Record video and optional slide deck (suggested 8 slides).
- LabLab event → Submit Project → fill title, short/long description, cover, video, presentation, tags, GitHub link, live URL.
- **Deadline:** Nov 8 2026 at 3:00 PM PST = Nov 9 at 4:00 AM PKT (as listed in the event).
- Optional Vultr Community showcase does NOT replace LabLab submission.

**Avoid:** uploading real passwords, customer data, source secrets, or sharing API keys in screenshots.
