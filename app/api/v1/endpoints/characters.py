from typing import Annotated, Any, List

from fastapi import APIRouter, HTTPException, status
from fastapi.params import Path
from fastapi_pagination import LimitOffsetPage, Page
from fastapi_pagination.cursor import CursorPage
from loguru import logger
from ulid import ULID as _python_ULID

from app.api.deps import DB
from app.crud.character import character_crud
from app.schemas.character import (
    Character,
    CharacterCreate,
    CharacterUpdate,
)
from app.schemas.ulid import ULID as _pydantic_ULID

router = APIRouter()


@router.get("/")
async def read_characters(
    *,
    db: DB,
) -> Page[Character]:
    """
    Retrieve characters.
    """
    import sqlalchemy as sa
    from fastapi_pagination.ext.sqlalchemy import paginate

    from app.models.character import Character as CharacterModel

    characters = await paginate(
        db, sa.select(CharacterModel).order_by(CharacterModel.id)
    )
    return characters


@router.post("/", response_model=Character, status_code=status.HTTP_201_CREATED)
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
            status_code=status.HTTP_409_CONFLICT,
            detail="A character with this name already exists",
        )

    character = await character_crud.create(db, obj_in=character_in)
    return character


@router.get("/{character_id}", response_model=Character)
async def read_character(
    *,
    db: DB,
    character_id: _python_ULID = Path(),
    # character_id: str,
) -> Any:
    """
    Get character by ID.
    """
    logger.debug(f"{type(character_id) = }")
    logger.debug(f"{repr(character_id) = }")
    # character = await character_crud.get(db, id=_python_ULID.from_str(character_id))
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
    character_id: Annotated[_python_ULID, Path()],
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

    logger.info(f"{await character.awaitable_attrs.dispositions = }")

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
    character_id: Annotated[_python_ULID, Path()],
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
