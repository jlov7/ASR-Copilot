# Quickstart (Pick Your Path)

> Need a zero-friction tour? Choose the flow that matches your role—each takes about a minute.

## 1. Instant Demo (no files, runs locally)
1. Install prerequisites (Python 3.11+, Node 18+, npm).
2. Create a virtual environment and install backend deps:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. Install frontend deps once:
   ```bash
   cd app/frontend
   npm install
   cd ../..
   ```
4. Launch the Safe Mode demo (seeds sample data, opens the UI):
   ```bash
   make demo
   ```
   This starts FastAPI at http://127.0.0.1:8000 and Vite at http://127.0.0.1:5173. Click **Instant Demo – no files needed** to preload realistic scenarios.

## 2. GitHub Codespaces (1‑click cloud devcontainer)
1. Click the **Open in Codespaces** badge in the README (or [launch directly](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=jlov7%2FASR-Copilot)).
2. Codespaces pre-installs Python, Node, and all extensions—wait for the post-create command to finish.
3. Run the combined workflow:
   ```bash
   make dev
   ```
4. Forward ports 8000 and 5173 (Codespaces prompts automatically) and open the forwarded URL. Load the Instant Demo or upload your own CSV/Markdown.

## 3. Hosted Safe Demo (Render Blueprint)
1. Create a free Render account if you don’t have one.
2. Click the **Deploy to Render** badge in the README (or [use this link](https://render.com/deploy?repo=https://github.com/jlov7/ASR-Copilot)).
3. Accept the defaults—`render.yaml` provisions both FastAPI and the Vite frontend with Safe Mode enforced.
4. Once deployed, open the Render URL. You’ll see the Instant Demo scenarios only; adapters stay in mock mode and no outbound calls are made.

### Need more paths?
- **Docker Compose**: `docker compose up` spins up FastAPI + frontend behind Traefik with Safe Mode on.
- **Local prod build**: `make release` builds both services and places exports in `./out/`.
- **Enable live adapters**: copy `.env.example` → `.env`, set tokens, and flip Safe Mode off from the UI once you’re ready for read-only integrations.
