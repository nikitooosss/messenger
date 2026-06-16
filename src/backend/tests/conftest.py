import os
from datetime import datetime

import pytest_asyncio
from dotenv import load_dotenv
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from backend.api.main import app
from backend.database.get_db import get_db
from backend.database.models import Base, User, Chat, ChatParticipant, Message, UserRole
from backend.services.auth import AuthService
from backend.services.chat import ChatService
from backend.services.chat_participant import ChatParticipantService
from backend.services.core.services_container import ServicesContainer
from backend.services.jwt import JWTService
from backend.services.message import MessageService
from backend.services.user import UserService
from backend.ws.manager import WSManager

load_dotenv()

TEST_DB_NAME = "messenger_test"


def build_test_dsn() -> str:
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{TEST_DB_NAME}"


@pytest_asyncio.fixture
async def test_engine():
    dsn = build_test_dsn()
    engine = create_async_engine(dsn, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _clean_db(test_engine):
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def db_session(test_engine):
    async with AsyncSession(test_engine, expire_on_commit=False) as session:
        yield session
        await session.close()


@pytest_asyncio.fixture
async def user_service(db_session: AsyncSession) -> UserService:
    return UserService(db=db_session)


@pytest_asyncio.fixture
async def auth_service(db_session: AsyncSession) -> AuthService:
    return AuthService(db=db_session)


@pytest_asyncio.fixture
async def chat_service(db_session: AsyncSession) -> ChatService:
    return ChatService(db=db_session)


@pytest_asyncio.fixture
async def message_service(db_session: AsyncSession) -> MessageService:
    return MessageService(db=db_session)


@pytest_asyncio.fixture
async def chat_participant_service(db_session: AsyncSession) -> ChatParticipantService:
    return ChatParticipantService(db=db_session)


@pytest_asyncio.fixture
async def jwt_service(db_session: AsyncSession) -> JWTService:
    return JWTService(db=db_session)


@pytest_asyncio.fixture
async def services_container(
    chat_service: ChatService,
    message_service: MessageService,
    chat_participant_service: ChatParticipantService,
    user_service: UserService,
) -> ServicesContainer:
    return ServicesContainer(
        chat_service=chat_service,
        message_service=message_service,
        chat_participant_service=chat_participant_service,
        user_service=user_service,
    )


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    def override_get_db():
        return db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def ws_manager() -> WSManager:
    return WSManager()


# --- Test data helpers ---


async def create_user_orm(
    db_session: AsyncSession,
    uniq_name: str = "testuser",
    name: str | None = "Test User",
    password_hash: str = "hashed_password",
    is_active: bool = False,
) -> User:
    user = User(
        uniq_name=uniq_name,
        name=name,
        password_hash=password_hash,
        is_active=is_active,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


async def create_chat_orm(
    db_session: AsyncSession,
    name: str = "Test Chat",
    is_group: bool = False,
) -> Chat:
    chat = Chat(name=name, is_group=is_group)
    db_session.add(chat)
    await db_session.commit()
    await db_session.refresh(chat)
    return chat


async def create_participant_orm(
    db_session: AsyncSession,
    chat_id: int,
    user_id: int,
    role: UserRole = UserRole.member,
) -> ChatParticipant:
    participant = ChatParticipant(chat_id=chat_id, user_id=user_id, role=role)
    db_session.add(participant)
    await db_session.commit()
    await db_session.refresh(participant)
    return participant


async def create_message_orm(
    db_session: AsyncSession,
    chat_id: int,
    user_id: int,
    content: str = "Hello, World!",
) -> Message:
    message = Message(
        chat_id=chat_id,
        user_id=user_id,
        content=content,
        created_at=datetime.utcnow(),
    )
    db_session.add(message)
    await db_session.commit()
    await db_session.refresh(message)
    return message
