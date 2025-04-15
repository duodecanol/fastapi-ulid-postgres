from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.character import Character
from app.schemas.character import CharacterCreate, CharacterUpdate


class CRUDCharacter(CRUDBase[Character, CharacterCreate, CharacterUpdate]):
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Character]:
        """
        Get a character by name.
        """
        result = await db.execute(select(Character).filter(Character.name == name))
        return result.scalars().first()

    async def get_multi_by_ids(
        self, db: AsyncSession, *, ids: List[UUID], skip: int = 0, limit: int = 100
    ) -> List[Character]:
        """
        Get multiple characters by IDs.
        """
        result = await db.execute(
            select(Character).filter(Character.id.in_(ids)).offset(skip).limit(limit)
        )
        return result.scalars().all()


character_crud = CRUDCharacter(Character)
