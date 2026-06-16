from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.database.get_db import get_db
from backend.services.user import UserService

from .routers import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    async for db in get_db():
        await UserService(db).reset_all_is_active()
        break
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(api_router)

STATIC_DIR = Path(__file__).resolve().parent.parent.parent / "static"

if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        index = STATIC_DIR / "index.html"
        if not index.is_file():
            return {"detail": "Frontend not built"}
        return FileResponse(index)
