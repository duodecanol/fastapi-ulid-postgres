import asyncio
import uuid
from typing import Any, AsyncGenerator, Dict, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.api.deps import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.crud.character import character_crud
from app.models.character import Character
from app.models.chat import ChatMessage, ChatSession
from app.models.user import User
from app.schemas.character import CharacterCreate
from app.schemas.user import UserCreate


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest_asyncio.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for each test case.
    """
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def _engine() -> AsyncGenerator[AsyncEngine, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    from app.core.database import Base
    from app.models import load_all_models
    from app.utils.database import create_database, drop_database  # noqa: WPS433

    print("Setting up test database".center(88, "="))

    load_all_models()

    await create_database()

    engine = create_async_engine(str(settings.DATABASE_URL), echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield engine
    finally:
        print("Tearing down test database".center(88, "="))
        await engine.dispose()
        await drop_database()


@pytest_asyncio.fixture
async def dbsession(
    _engine: AsyncEngine,
) -> AsyncGenerator[AsyncSession, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param _engine: current engine.
    :yields: async session.
    """
    connection = await _engine.connect()
    trans = await connection.begin()

    session_maker = async_sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        yield session
    finally:
        await session.close()
        await trans.rollback()
        await connection.close()


@pytest_asyncio.fixture
def fastapi_app(
    dbsession: AsyncSession,
) -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    from app.main import get_app

    application = get_app()
    application.dependency_overrides[get_db] = lambda: dbsession
    return application  # noqa: WPS331


@pytest_asyncio.fixture
async def client(
    fastapi_app: FastAPI,
    anyio_backend: Any,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def test_user(dbsession: AsyncSession) -> User:
    """
    Create a test user.
    """
    user_in = UserCreate(
        username="testuser",
        email="test@example.com",
        password="password123",
        password_confirm="password123",
    )

    # Convert SecretStr to plain string for hashing
    password = user_in.password.get_secret_value()

    user = User(
        id=uuid.uuid4(),
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(password),
    )

    dbsession.add(user)
    await dbsession.commit()
    await dbsession.refresh(user)

    return user


@pytest_asyncio.fixture(scope="function")
async def test_character(dbsession: AsyncSession) -> Character:
    """
    Create a test character.
    """
    character_in = CharacterCreate(
        name="Test Character",
        description="A character for testing",
        default_outfit="Default outfit",
        extra_variables={"key": "value"},
    )

    character = await character_crud.create(dbsession, obj_in=character_in)
    return character


@pytest_asyncio.fixture(scope="function")
async def test_chat_session(
    dbsession: AsyncSession, test_user: User, test_character: Character
) -> ChatSession:
    """
    Create a test chat session.
    """
    chat_session = ChatSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        character_id=test_character.id,
        session_type="dialogue",
        intimacy_level=1,
    )

    dbsession.add(chat_session)
    await dbsession.commit()
    await dbsession.refresh(chat_session)

    return chat_session


@pytest_asyncio.fixture(scope="function")
async def test_chat_message(
    dbsession: AsyncSession, test_chat_session: ChatSession
) -> ChatMessage:
    """
    Create a test chat message.
    """
    chat_message = ChatMessage(
        id=uuid.uuid4(),
        chat_session_id=test_chat_session.id,
        type="user",
        content="Hello, this is a test message",
    )

    dbsession.add(chat_message)
    await dbsession.commit()
    await dbsession.refresh(chat_message)

    return chat_message


@pytest_asyncio.fixture(scope="function")
async def token_headers(test_user: User) -> Dict[str, str]:
    """
    Create token headers for authentication.
    """
    access_token = create_access_token(subject=str(test_user.id))
    return {"Authorization": f"Bearer {access_token}"}


@pytest.mark.anyio
async def test_client(client):
    print(client)
