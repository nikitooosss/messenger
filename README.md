# messenger

Telegram-style messenger SPA: FastAPI backend (REST + WebSocket), React + TypeScript frontend, PostgreSQL.

## Quick start with Docker

```bash
cp docker/.env.example .env
docker compose up --build
```

After the build finishes (2-3 minutes the first time), open:

- App: http://localhost:8000

Register a new user through the UI and start chatting.

To stop: `Ctrl+C` then `docker compose down`. The database is preserved in a Docker volume.

To reset everything (including the database): `docker compose down -v`.

## Environment variables (`.env`)

| Variable | Default | Description |
| --- | --- | --- |
| `POSTGRES_USER` | `postgres` | PostgreSQL user |
| `POSTGRES_PASSWORD` | `postgres` | PostgreSQL password |
| `POSTGRES_DB_NAME` | `messenger` | PostgreSQL database name |
| `SECRET_KEY` | `change-me-...` | JWT signing key. **Replace in production.** Generate with `openssl rand -hex 32`. |
| `ALGORITHM` | `HS256` | JWT algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT lifetime in minutes |

## Local development (without Docker)

Backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
cp docker/.env.example .env  # then point POSTGRES_HOST to localhost
alembic upgrade head
uvicorn backend.api.main:app --reload --port 8000
```

Frontend (separate terminal):

```bash
cd src/frontend
npm install
npm run dev
```

Open http://localhost:5173. Vite dev server proxies `/api/*` to the backend on port 8000.
