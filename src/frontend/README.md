# Messenger — Frontend

A Telegram-style React SPA that talks to the FastAPI backend in `../src/backend/`.

## Stack

- Vite + React 18 + TypeScript
- TanStack Router (code-based) + TanStack Query
- Native WebSocket (wrapped in `WebSocketProvider`)
- Tailwind CSS (Telegram palette under the `tg.*` namespace)

## Run

```bash
npm install
npm run dev          # http://localhost:5173
```

The Vite dev server proxies `/auth`, `/user`, `/chat`, `/message`, `/chat_participant` and `/ws` to `http://localhost:8000` so the HttpOnly `access_token` cookie is automatically attached to REST and WebSocket requests.

Start the backend separately (e.g. `uvicorn backend.api.main:app --reload --port 8000 --app-dir ../src`).

## Build

```bash
npm run build        # tsc -b && vite build
```

## Project structure

- `src/lib/` — REST client, query keys, time formatting
- `src/types/` — model + WS event types
- `src/ws/` — WebSocket provider + event dispatcher into TanStack Query cache
- `src/auth/` — login/register, current-user query, route guard
- `src/features/chats/` — sidebar, chat list, create-chat dialog
- `src/features/messages/` — message view, bubble, input (typing debounce + optimistic send), typing indicator
- `src/features/participants/` — member list + add-member dialog
- `src/features/presence/` — online/typing bus
- `src/components/` — shared UI primitives
