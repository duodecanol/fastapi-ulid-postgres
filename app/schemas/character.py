from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, EmailStr

from .ulid import ULID


# Character schemas
class CharacterBase(BaseModel):
    name: str
    description: str
    default_outfit: Optional[str] = None
    extra_variables: Optional[Dict[str, Any]] = None


class CharacterCreate(CharacterBase):
    pass


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    default_outfit: Optional[str] = None
    extra_variables: Optional[Dict[str, Any]] = None


class CharacterInDBBase(CharacterBase):
    id: ULID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Character(CharacterInDBBase):
    pass
