# CrossCoach

AI-powered skill cross-training companion to log activities across domains and generate weekly insights.

## Stack
- Frontend: React + Vite + TailwindCSS
- Backend: FastAPI (Python)
- Database: Postgres
- Analytics: Python service computing correlations
- AI: OpenAI-compatible API for summaries and insights

## Quick Start (Docker)
1. Copy `env.example` to `.env` and adjust values
2. Build and start services:

```bash
docker compose up --build
```

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## Services
- backend: FastAPI app exposing REST endpoints for users, logs, and insights
- analytics: background worker computing correlations weekly and summarizing journals

## Local Development
- Backend hot-reload is configured via `uvicorn` in the Dockerfile
- Frontend uses Vite dev server

## Database Schema (MVP)
- `users` (id, email, name)
- `logs` (user_id, date, domain, value, metrics JSON, note)
- `insights` (user_id, week_start, summary, correlations)

## Seed Data
Run the seed script after services are up:

```bash
docker compose exec backend python -m app.scripts.seed
```

## Environment Variables
See `env.example` for defaults. Key values:
- `DATABASE_URL`
- `OPENAI_API_KEY`
- `OPENAI_API_BASE`
- `OPENAI_MODEL`
- `VITE_API_BASE_URL`

## License
MIT