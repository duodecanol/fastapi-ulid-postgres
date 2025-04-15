from pydantic import PostgresDsn
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings


async def create_database() -> None:
    """Create a database."""
    db_url = PostgresDsn.build(
        scheme=settings.DATABASE_URL.scheme,
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        path="postgres",
    )
    engine = create_async_engine(str(db_url), isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        database_existence = await conn.execute(
            text(
                f"SELECT 1 FROM pg_database WHERE datname='{settings.POSTGRES_DB}'",  # noqa: E501, S608
            ),
        )
        database_exists = database_existence.scalar() == 1

    if database_exists:
        await drop_database()

    async with engine.connect() as conn:  # noqa: WPS440
        await conn.execute(
            text(
                f'CREATE DATABASE "{settings.POSTGRES_DB}" ENCODING "utf8" TEMPLATE template1',  # noqa: E501
            ),
        )


async def drop_database() -> None:
    """Drop current database."""
    # Create a new PostgresDsn with the specified database name
    db_url = PostgresDsn.build(
        scheme=settings.DATABASE_URL.scheme,
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT,
        path="postgres",
    )
    engine = create_async_engine(str(db_url), isolation_level="AUTOCOMMIT")

    async with engine.connect() as conn:
        disc_users = (
            "SELECT pg_terminate_backend(pg_stat_activity.pid) "  # noqa: S608
            "FROM pg_stat_activity "
            f"WHERE pg_stat_activity.datname = '{settings.POSTGRES_DB}' "
            "AND pid <> pg_backend_pid();"
        )
        await conn.execute(text(disc_users))
        await conn.execute(text(f'DROP DATABASE "{settings.POSTGRES_DB}"'))
