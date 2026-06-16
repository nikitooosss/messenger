# syntax=docker/dockerfile:1.7

# ---- Stage 1: build frontend ----
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY src/frontend/package.json src/frontend/package-lock.json* ./
RUN npm ci || npm install
COPY src/frontend ./
RUN npm run build

# ---- Stage 2: backend runtime ----
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src ./src
COPY alembic ./alembic
COPY alembic.ini ./

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir \
        "fastapi[standard]>=0.136.1" \
        "sqlalchemy>=2.0.49" \
        "asyncpg>=0.31.0" \
        "alembic>=1.18.4" \
        "pyjwt>=2.12.1" \
        "pwdlib[argon2]>=0.3.0" \
        "dotenv>=0.9.9" \
        "websockets==13.1"

COPY --from=frontend-builder /app/frontend/dist /app/static

COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000
CMD ["/app/entrypoint.sh"]
