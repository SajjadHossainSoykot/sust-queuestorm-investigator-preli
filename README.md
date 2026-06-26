# SUST QueueStorm Investigator

A full-stack hackathon project for the **SUST CSE Carnival 2026 · Codex Community Hackathon · Online Preliminary Round**.

This repository contains both the backend API and the frontend dashboard for **QueueStorm Investigator**, an AI-assisted SupportOps copilot for analyzing digital finance customer complaints.

The system accepts a customer support ticket, checks the complaint against recent transaction history, identifies the most relevant transaction, classifies the case, evaluates evidence consistency, routes the case to the correct department, and prepares a safe customer-facing response for support agents.

> This project does **not** execute financial operations such as refund, reversal, settlement, account unblock, or real payment actions. It only provides structured investigation support for human review.

---

## Live Links

| Part | URL |
|---|---|
| Frontend | `https://queuestorm-investigator-preli.vercel.app` |
| Backend API | `https://sust-queuestorm-investigator.vercel.app` |
| Health Check | `https://sust-queuestorm-investigator.vercel.app/health` |
| Analyze Endpoint | `POST /analyze-ticket` |

---

## Repository Structure

```txt
sust-queuestorm-investigator-preli/
├── backend/
│   ├── app/
│   │   ├── analyzer.py              # Rule engine, transaction matching, LLM pipeline
│   │   ├── config.py                # Environment variable configuration
│   │   ├── main.py                  # FastAPI app, endpoints, exception handlers
│   │   ├── models.py                # Pydantic request/response schemas and enums
│   │   └── safety.py                # Post-generation safety checks and sanitizers
│   ├── .dockerignore
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile
│   ├── README.md                    # Backend-specific documentation
│   ├── RUNBOOK.md                   # Operations runbook
│   ├── SUST_Preli_Sample_Cases.json # Official public sample case pack
│   ├── requirements.txt
│   ├── run.py                       # Uvicorn entry point (auto port-kill on start)
│   ├── sample_request.json          # Example request for manual API testing
│   ├── test_api.py                  # FastAPI TestClient endpoint tests
│   └── verify_sample_cases.py       # Verifier for public sample cases
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js            # API client with normalizeBaseUrl helper
│   │   ├── components/
│   │   │   └── Footer.jsx           # Footer with team credits and links
│   │   ├── data/
│   │   │   └── examples.js          # Sample ticket payloads and form options
│   │   ├── App.jsx                  # Main dashboard component
│   │   ├── main.jsx                 # React entry point
│   │   └── styles.css               # Full custom CSS design system
│   ├── .dockerignore
│   ├── .env.example
│   ├── .gitignore
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   └── package-lock.json
│
├── .gitignore
├── README.md
├── run_backend.sh
└── run_frontend.sh
```

---

## Main Features

### Backend

- FastAPI-based backend service
- `GET /health` and `POST /analyze-ticket` endpoints
- Pydantic request and response validation with strict enum types
- Deterministic rule-based investigation engine for all critical fields
- Optional Gemini-powered text polishing for natural-language response fields
- Safe fallback templates when Gemini is unavailable or times out
- Programmatic safety sanitizer (`safety.py`) applied to all output text
- CORS enabled for frontend integration
- Automatic port conflict resolution on startup (`run.py` kills stale processes)
- Docker-ready backend setup

### Frontend

- Vite + React frontend with a premium dark-mode glassmorphism design
- Runtime API base URL switcher with localStorage persistence (no `.env` restart required)
- Health check button with live status pill
- Ticket analysis form with visual fields for all ticket properties
- Raw JSON editor mode with live validation
- Pre-loaded sample ticket cases for quick testing
- Dynamic transaction history input (add / remove entries)
- Structured result dashboard: stats grid, evidence verdict, severity, routing details
- Text panels for agent summary, recommended action, and customer reply
- Reason codes displayed as pills
- Copy full JSON response to clipboard
- Collapsible raw JSON viewer
- Footer component with team credits and GitHub links
- Fully responsive layout (desktop, tablet, mobile)
- Vercel-ready deployment

---

## API Endpoints

### Health Check

```http
GET /health
```

Example:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

### Analyze Ticket

```http
POST /analyze-ticket
```

Example:

```bash
curl -X POST http://localhost:8000/analyze-ticket \
  -H "Content-Type: application/json" \
  --data-binary @backend/sample_request.json
```

The frontend uses this endpoint to send ticket data and display the investigation response.

---

## Environment Setup

### Backend Environment

Create a `.env` file inside the `backend/` folder:

```bash
cp backend/.env.example backend/.env
```

Example backend `.env`:

```env
HOST=0.0.0.0
PORT=8000
DEBUG=True
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
REQUEST_TIMEOUT_SEC=15.0
```

`GEMINI_API_KEY` is optional. If it is not provided, the backend will still run using the local deterministic rule engine.

---

### Frontend Environment

Create a `.env` file inside the `frontend/` folder:

```bash
cp frontend/.env.example frontend/.env
```

For local backend testing:

```env
VITE_API_BASE_URL=http://localhost:8000
```

For deployed backend:

```env
VITE_API_BASE_URL=https://sust-queuestorm-investigator.vercel.app
```

> **Tip:** The frontend also provides a runtime API URL switcher in the hero panel. You can change the API base URL directly from the browser without editing `.env` or restarting the dev server. The URL is saved in `localStorage` and persists across page refreshes.

---

## Run the Project Locally

You can run the backend and frontend separately using the provided shell scripts.

### Run Backend

From the root folder:

```bash
chmod +x run_backend.sh
./run_backend.sh
```

The backend will run at:

```txt
http://localhost:8000
```

Health check:

```txt
http://localhost:8000/health
```

> **Note:** The backend `run.py` automatically detects and terminates any stale process occupying the configured port before starting Uvicorn. You no longer need to manually kill port conflicts.

---

### Run Frontend

Open another terminal and run:

```bash
chmod +x run_frontend.sh
./run_frontend.sh
```

The frontend will run at:

```txt
http://localhost:5173
```

---

## Manual Run Commands

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Alternative:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Deployment Guide

### Deploy Backend

The backend can be deployed on Render, Railway, Vercel serverless, AWS, or any Python-compatible hosting platform.

For a common Render deployment:

| Setting | Value |
|---|---|
| Root Directory | `backend` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python run.py` |

Add environment variables from `backend/.env.example` in the hosting dashboard.

---

### Deploy Frontend on Vercel

For the frontend deployment:

| Setting | Value |
|---|---|
| Root Directory | `frontend` |
| Framework Preset | Vite |
| Build Command | `npm run build` |
| Output Directory | `dist` |

Add this environment variable in Vercel:

```env
VITE_API_BASE_URL=https://your-deployed-backend-url.com
```

Then redeploy the frontend.

---

### Deploy with Docker

Both the backend and frontend include Dockerfiles.

**Backend:**

```bash
cd backend
docker build -t queuestorm-backend .
docker run -p 8000:8000 --env-file .env queuestorm-backend
```

**Frontend:**

```bash
cd frontend
docker build \
  --build-arg VITE_API_BASE_URL=https://your-backend-url.com \
  -t queuestorm-frontend .
docker run -p 3000:80 queuestorm-frontend
```

The frontend Dockerfile uses a multi-stage build: Node 20 builds the Vite app, then nginx serves the static files with SPA fallback. Override `VITE_API_BASE_URL` at build time via `--build-arg`.

---

## Development Workflow

1. Start the backend with `./run_backend.sh`.
2. Confirm the backend is working at `http://localhost:8000/health`.
3. Set `frontend/.env` to `VITE_API_BASE_URL=http://localhost:8000` (or use the runtime URL switcher in the UI).
4. Start the frontend with `./run_frontend.sh`.
5. Open `http://localhost:5173`.
6. Select a sample ticket or fill in the form.
7. Click **Analyze Ticket** and inspect the structured response.
8. Use **Copy JSON** to export the result or expand **Raw JSON** for the full payload.

---

## Troubleshooting

### Frontend cannot connect to backend

Check that the backend is running:

```bash
curl http://localhost:8000/health
```

Check `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

Or use the **runtime API URL switcher** in the hero panel to point to a different backend without restarting the dev server.

Restart the frontend server after changing `.env` (not needed if using the runtime switcher).

---

### Port already in use

The backend `run.py` now **automatically kills stale processes** on the configured port before starting. If you still encounter issues:

For backend port `8000`:

```bash
lsof -ti:8000 | xargs kill -9
```

For frontend port `5173`:

```bash
lsof -ti:5173 | xargs kill -9
```

Then run the scripts again.

---

### Missing Python packages

Run:

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Missing frontend packages

Run:

```bash
cd frontend
npm install
```

---

## Important Git Notes

Do not commit these files or folders:

```txt
backend/.env
frontend/.env
frontend/node_modules/
frontend/dist/
backend/.venv/
.DS_Store
__pycache__/
```

Only commit `.env.example` files, not real `.env` files.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vite, React, Lucide React icons |
| Backend | FastAPI, Pydantic v2, Uvicorn |
| AI / LLM | Optional Google Gemini API (gemini-2.5-flash) |
| HTTP Client | HTTPX |
| Styling | Custom CSS (dark-mode glassmorphism design system) |
| Deployment | Vercel (frontend + backend serverless) / Render / Docker |

---

## Team

**Team !BlackBox**

| Role | Member | GitHub |
|---|---|---|
| API Developer | Julfikar Jim | [@md-julfikar](https://github.com/md-julfikar) |
| Frontend Developer | Sajjad Hossain Soykot | [@SajjadHossainSoykot](https://github.com/SajjadHossainSoykot) |
| Team Member | Abu Ubaida | [@ubaida01](https://github.com/ubaida01) |

---

## Project Status

This project is prepared as a complete full-stack setup:

- Backend API is inside `backend/`
- Frontend app is inside `frontend/`
- Root README explains the full project
- Shell scripts simplify local running
- Frontend connects to backend using `VITE_API_BASE_URL` or the runtime URL switcher
- Auto port-kill on backend startup prevents stale-process conflicts
- Footer credits team members with GitHub links
