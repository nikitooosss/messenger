from .database import async_session_maker

async def get_db():
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()
