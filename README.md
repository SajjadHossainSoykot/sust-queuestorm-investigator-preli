# SUST QueueStorm Investigator

A full-stack hackathon project for the **SUST CSE Carnival 2026 · Codex Community Hackathon · Online Preliminary Round**.

This repository contains both the backend API and the frontend dashboard for **QueueStorm Investigator**, an AI-assisted SupportOps copilot for analyzing digital finance customer complaints.

The system accepts a customer support ticket, checks the complaint against recent transaction history, identifies the most relevant transaction, classifies the case, evaluates evidence consistency, routes the case to the correct department, and prepares a safe customer-facing response for support agents.

> This project does **not** execute financial operations such as refund, reversal, settlement, account unblock, or real payment actions. It only provides structured investigation support for human review.

---

## Live Links

| Part | URL |
|---|---|
| Frontend | Add your deployed frontend URL here |
| Backend API | `https://sust-queuestorm-investigator.vercel.app` |
| Health Check | `https://sust-queuestorm-investigator.vercel.app/health` |
| Analyze Endpoint | `POST /analyze-ticket` |

---

## Repository Structure

```txt
sust-queuestorm-investigator-preli/
├── backend/
│   ├── app/
│   │   ├── analyzer.py
│   │   ├── config.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── safety.py
│   ├── .env.example
│   ├── Dockerfile
│   ├── README.md
│   ├── RUNBOOK.md
│   ├── requirements.txt
│   ├── run.py
│   ├── sample_request.json
│   ├── test_api.py
│   └── verify_sample_cases.py
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js
│   │   ├── data/
│   │   │   └── examples.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── .env.example
│   ├── index.html
│   ├── package.json
│   ├── package-lock.json
│   └── vercel.json
│
├── README.md
├── run_backend.sh
└── run_frontend.sh
```

---

## Main Features

### Backend

- FastAPI-based backend service
- `GET /health` endpoint
- `POST /analyze-ticket` endpoint
- Pydantic request and response validation
- Deterministic rule-based investigation engine
- Optional Gemini-powered text polishing
- Safe fallback when Gemini is unavailable
- CORS enabled for frontend integration
- Docker-ready backend setup

### Frontend

- Vite + React frontend
- API base URL configurable using `.env`
- Health check button
- Ticket analysis form
- JSON editor mode
- Sample ticket cases
- Transaction history input
- Structured result dashboard
- Copy JSON response support
- Vercel-ready deployment configuration

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

Important: after changing a Vite `.env` file, restart the frontend development server.

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

## Important Git Notes

Do not commit these files or folders:

```txt
backend/.env
frontend/.env
frontend/node_modules/
backend/.venv/
.DS_Store
__pycache__/
```

Only commit `.env.example` files, not real `.env` files.

Recommended root `.gitignore` entries:

```gitignore
# Environment files
.env
backend/.env
frontend/.env

# Python
backend/.venv/
__pycache__/
*.pyc

# Node / Vite
frontend/node_modules/
frontend/dist/

# OS files
.DS_Store

# Logs
*.log
```

---

## Development Workflow

1. Start the backend with `./run_backend.sh`.
2. Confirm the backend is working at `http://localhost:8000/health`.
3. Set `frontend/.env` to `VITE_API_BASE_URL=http://localhost:8000`.
4. Start the frontend with `./run_frontend.sh`.
5. Open `http://localhost:5173`.
6. Submit a sample ticket from the frontend.
7. Check the structured response from the backend.

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

Restart the frontend server after changing `.env`.

---

### Port already in use

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

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vite, React |
| Backend | FastAPI, Pydantic, Uvicorn |
| AI / LLM | Optional Gemini API |
| Styling | Custom CSS |
| Deployment | Vercel / Render / Docker-compatible hosting |

---

## Project Status

This project is prepared as a complete full-stack setup:

- Backend API is inside `backend/`
- Frontend app is inside `frontend/`
- Root README explains the full project
- Shell scripts simplify local running
- Frontend connects to backend using `VITE_API_BASE_URL`

