import sqlalchemy as sa
import sqlalchemy.sql.schema as sa_schema
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    declared_attr,
    sessionmaker,
)

from app.core.config import settings

engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=True,
    future=True,
)

SessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

# https://til.cybertec-postgresql.com/post/2019-09-02-Postgres-Constraint-Naming-Convention/
postgres_naming_convention: sa_schema._NamingSchemaTD = {
    "pk": "%(table_name)s_pkey",
    "uq": "%(table_name)s_%(column_0_N_name)s_key",
    "ix": "%(table_name)s_%(column_0_N_name)s_idx",
    "ck": "%(table_name)s_%(constraint_name)s_check",
    "fk": "%(table_name)s_%(column_0_name)s_%(referred_table_name)s_fkey",
}


meta = sa.MetaData(naming_convention=postgres_naming_convention)


class Base(AsyncAttrs, DeclarativeBase):
    """Base for all models."""

    metadata = meta

    @declared_attr.directive
    def __tablename__(cls) -> str:
        sn = [c if c.islower() else f"_{c.lower()}" for c in cls.__name__]
        return "".join(sn)[1:]


async def get_db():
    """
    Dependency function that yields db sessions
    """
    session: AsyncSession
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.commit()
            await session.close()
