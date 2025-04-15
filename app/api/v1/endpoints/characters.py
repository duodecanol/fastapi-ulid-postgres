from typing import Any, List

from fastapi import APIRouter, HTTPException, status
from loguru import logger

from app.api.deps import DB
from app.crud.character import character_crud
from app.models.types import ULIDType
from app.schemas.character import (
    Character,
    CharacterCreate,
    CharacterUpdate,
)
from app.schemas.ulid import ULID

router = APIRouter()


@router.get("/", response_model=List[Character])
async def read_characters(
    *,
    db: DB,
    skip: int = 0,
    limit: int = 100,
    name: str = None,
) -> Any:
    """
    Retrieve characters.
    """
    if name:
        characters = await character_crud.get_by_name(
            db, name=name, skip=skip, limit=limit
        )
    else:
        characters = await character_crud.get_multi(db, skip=skip, limit=limit)
    return characters


@router.post("/", response_model=Character)
async def create_character(
    *,
    db: DB,
    character_in: CharacterCreate,
) -> Any:
    """
    Create new character.
    Admin only.
    """
    character = await character_crud.get_by_name(db, name=character_in.name)
    if character:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A character with this name already exists",
        )

    character = await character_crud.create(db, obj_in=character_in)
    return character


@router.get("/{character_id}", response_model=Character)
async def read_character(
    *,
    db: DB,
    character_id: str,
    # character_id: ULID,
) -> Any:
    """
    Get character by ID.
    """
    character = await character_crud.get(db, id=character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found",
        )
    return character


@router.put("/{character_id}", response_model=Character)
async def update_character(
    *,
    db: DB,
    character_id: str,
    character_in: CharacterUpdate,
) -> Any:
    """
    Update a character.
    Admin only.
    """
    character = await character_crud.get(db, id=character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found",
        )

    logger.info(f"{character.dispositions = }")

    # Check if name is being updated and if it already exists
    if character_in.name and character_in.name != character.name:
        existing = await character_crud.get_by_name(db, name=character_in.name)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A character with this name already exists",
            )

    character = await character_crud.update(db, db_obj=character, obj_in=character_in)
    logger.info(f"{character = }")
    return character


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_character(
    *,
    db: DB,
    character_id: str,
) -> None:
    """
    Delete a character.
    Admin only.
    """
    character = await character_crud.get(db, id=character_id)
    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found",
        )

    await character_crud.delete(db, id=character_id)
