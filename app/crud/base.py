from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base
from app.schemas.ulid import UlidType
from app.utils.datetime import utc_now_aware

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: UlidType) -> Optional[ModelType]:
        """
        Get a single record by ID.
        """
        result = await db.execute(select(self.model).filter(self.model.id == id))
        return result.scalars().first()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple records.
        """
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new record.
        """
        logger.debug(f"=== CREATE {self.model.__name__}")
        async with db.begin_nested():
            db_obj = self.model(
                **obj_in.model_dump(exclude_none=True, exclude_unset=True)
            )
            db.add(db_obj)

        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """
        Update a record.
        """
        refined_update_fields = obj_in.model_dump(
            exclude_none=True,
            exclude_unset=True,
        )
        logger.debug(f"{refined_update_fields=}")
        for k in refined_update_fields.keys():
            logger.debug(f"{type(db_obj).__name__}.{k} = {db_obj.__getattribute__(k)}")
        # UPDATE FIELDS
        async with db.begin_nested():
            logger.debug(f"=== UPDATE {type(db_obj).__name__}")
            for k, v in refined_update_fields.items():
                db_obj.__setattr__(k, v)

        for k in refined_update_fields.keys():
            logger.debug(f"{type(db_obj).__name__}.{k} = {db_obj.__getattribute__(k)}")

        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: UlidType) -> ModelType:
        """
        Delete a record.
        """
        obj = await db.get(self.model, id)
        await db.delete(obj)
        await db.commit()
        return obj

    async def delete(self, db: AsyncSession, *, id: UlidType) -> None:
        """
        Delete a record.
        """
        async with db.begin_nested():
            obj = await db.get(self.model, id)
            logger.debug(f"=== DELETE {type(obj).__name__}")
            await db.delete(obj)

        logger.info(f"=== SUCCESSFUL DELETE {type(obj).__name__}")

    async def quasi_delete(self, db: AsyncSession, *, id: UlidType) -> None:
        """
        Quasi-delete a record.
        """
        async with db.begin_nested():
            obj = await db.get(self.model, id)
            logger.debug(
                f"=== quasi-DELETE {type(obj).__name__} by setting column `deleted_at`"
            )
            obj.deleted_at = utc_now_aware()
