#!/usr/bin/env sh
set -e

echo "[entrypoint] Running alembic upgrade head..."
alembic upgrade head

echo "[entrypoint] Starting uvicorn..."
exec uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --proxy-headers
