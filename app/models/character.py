from datetime import UTC, datetime
from typing import List, Optional

import sqlalchemy as sa
import ulid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

from .types import ULIDType


class Disposition(Base):
    id: Mapped[ulid.ULID] = mapped_column(
        ULIDType(),
        nullable=False,
        primary_key=True,
        default=ulid.ULID,
        server_default=sa.text("gen_ulid()"),
    )
    category: Mapped[str] = mapped_column(sa.String, nullable=False)
    trait: Mapped[str] = mapped_column(sa.String, nullable=False)

    # Foreign key to Character
    character_id: Mapped[ulid.ULID] = mapped_column(
        ULIDType(), sa.ForeignKey("character.id"), nullable=False
    )

    # Relationship back to Character
    character: Mapped["Character"] = relationship(
        "Character", back_populates="dispositions"
    )


class Character(Base):
    id: Mapped[ulid.ULID] = mapped_column(
        ULIDType(),
        nullable=False,
        primary_key=True,
        default=ulid.ULID,
        server_default=sa.text("gen_ulid()"),
    )
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    description: Mapped[str] = mapped_column(sa.Text, nullable=False)
    default_outfit: Mapped[str] = mapped_column(sa.Text, nullable=True)
    extra_variables: Mapped[dict] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True), default=datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.TIMESTAMP(timezone=True),
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )

    # Relationships
    dispositions: Mapped[List["Disposition"]] = relationship(
        "Disposition", back_populates="character"
    )
