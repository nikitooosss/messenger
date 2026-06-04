from sqlalchemy.ext.asyncio import create_async_engine

from backend.config import POSTGRES_DSN

engine = create_async_engine(POSTGRES_DSN, echo=True, future=True)
