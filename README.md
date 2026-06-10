# Kalibr

AI-powered resume tailoring, job search, and application tracking platform.

## Monorepo Structure

```
/kalibr
  /frontend        ← React 18 + Vite 5 + Tailwind CSS v4
  /backend         ← FastAPI 0.111, Python 3.12
  /workers         ← Celery workers (separate from backend)
  docker-compose.yml
  .env.example
  .gitignore
  README.md
```

## Prerequisites

- Docker & Docker Compose v2
- Node.js 20+ (for local frontend dev)
- Python 3.12+ (for local backend dev)

## Quick Start

1. Copy the environment template and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

2. Start all services with Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. Access the services:
   | Service  | URL                           |
   |----------|-------------------------------|
   | Frontend | http://localhost:5173         |
   | Backend  | http://localhost:8000         |
   | API Docs | http://localhost:8000/docs    |
   | Redis    | localhost:6379                |

## Local Development

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

### Workers
```bash
cd workers
celery -A celery_app worker --loglevel=info
```

## Tech Stack

| Layer    | Technology                                      |
|----------|-------------------------------------------------|
| Frontend | React 18, Vite 5, Tailwind CSS v4, Zustand      |
| Backend  | FastAPI 0.111, Python 3.12, Pydantic v2         |
| Workers  | Celery, Redis                                   |
| Auth     | Firebase Authentication                         |
| Database | Supabase (PostgreSQL)                           |
| AI       | NVIDIA NIM (via OpenAI-compatible API)          |
| Email    | Resend                                          |
