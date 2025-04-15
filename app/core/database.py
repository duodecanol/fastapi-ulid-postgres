import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, create_async_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    declarative_base,
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

meta = sa.MetaData()


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
