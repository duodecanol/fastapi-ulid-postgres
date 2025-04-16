import uuid
from typing import Literal

import ulid
from sqlalchemy import types, util
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.type_api import UserDefinedType
from sqlalchemy_utils.types.scalar_coercible import ScalarCoercible
from ulid import ULID as _python_ULID


class _ULIDScalarCoercible(ScalarCoercible):
    @staticmethod
    def _coerce(value) -> ulid.ULID | None:
        if not value:
            return None

        if isinstance(value, str):
            try:
                value = ulid.ULID.from_str(value)
            except (TypeError, ValueError):
                value = ulid.ULID.from_hex(value)

            return value

        if isinstance(value, int):
            return ulid.ULID.from_int(value)

        if isinstance(value, bytes):
            return ulid.ULID.from_bytes(value)

        if isinstance(value, uuid.UUID):
            return ulid.ULID.from_uuid(value)

        if not isinstance(value, ulid.ULID):
            return ulid.ULID.from_bytes(value.bytes)

        return value


class UserDefinedULIDType(_ULIDScalarCoercible, UserDefinedType):
    cache_ok = True

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return super().__repr__()

    def get_col_spec(self, **kw) -> str:
        """DB의 column type 명칭을 제공한다"""
        return "ulid"

    def bind_processor(self, dialect):
        def process(value) -> str | None:
            if value is None:
                return value

            if not isinstance(value, ulid.ULID):
                value = self._coerce(value)

            return str(value)
            # return value.bytes

        return process

    def result_processor(self, dialect, coltype):
        def process(value) -> ulid.ULID | None:
            if value is None:
                return value

            return self._coerce(value)

        return process


class DifferedULIDType(_ULIDScalarCoercible, types.TypeDecorator):
    """
    Stores a ULID in the database as a native column type
    """

    cache_ok = True

    # impl = postgresql.UUID(as_uuid=True)
    # impl = postgresql.CHAR(26)
    # impl = postgresql.BYTEA(16)
    impl: postgresql.UUID | postgresql.CHAR | postgresql.BYTEA

    python_type = _python_ULID

    def __init__(self, column_type: Literal["uuid", "byte", "char"] = "byte", **kwargs):
        self.column_type = column_type
        match column_type:
            case "uuid":
                self.impl = postgresql.UUID(as_uuid=True)
            case "byte":
                self.impl = postgresql.BYTEA(16)
            case "char":
                self.imp = postgresql.CHAR(26)
            case _:
                raise ValueError(f"Invalid param `column_type` [{column_type}]")

    def __repr__(self):
        return util.generic_repr(self)

    def load_dialect_impl(self, dialect):
        if self.column_type == "char":
            return dialect.type_descriptor(types.UnicodeText)
        return dialect.type_descriptor(self.impl)

    def process_bind_param(self, value, dialect) -> bytes | None:
        if value is None:
            return value

        if not isinstance(value, ulid.ULID):
            value = self._coerce(value)

        match self.column_type:
            case "uuid":
                return str(value)
            case "byte":
                return value.bytes
            case "char":
                return str(value)

    def process_result_value(self, value, dialect) -> ulid.ULID | None:
        if value is None:
            return value

        return self._coerce(value)


ULIDType = UserDefinedULIDType
# ULIDType = DifferedULIDType
