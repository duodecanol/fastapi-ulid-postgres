from __future__ import annotations

import uuid
from typing import Literal, Optional, TypeVar, overload

import ulid
from sqlalchemy import types, util
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql.type_api import Emulated, TypeEngine, UserDefinedType
from sqlalchemy_utils.types.scalar_coercible import ScalarCoercible
from ulid import ULID as _python_ULID

_UUID_RETURN = TypeVar("_UUID_RETURN", str, _python_ULID)


class _CoerceULIDMixin:
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


class Ulid(Emulated, TypeEngine[_UUID_RETURN]):
    __visit_name__ = "ulid"

    collation: Optional[str] = None

    @overload
    def __init__(
        self: Ulid[_python_ULID],
        as_ulid: Literal[True] = ...,
        native_ulid: bool = ...,
    ): ...

    @overload
    def __init__(
        self: Ulid[str],
        as_ulid: Literal[False] = ...,
        native_ulid: bool = ...,
    ): ...

    def __init__(self, as_ulid: bool = True, native_ulid: bool = True):
        """Construct a :class:`_sqltypes.Uuid` type.

        :param as_uuid=True: if True, values will be interpreted
         as Python uuid objects, converting to/from string via the
         DBAPI.


        :param native_uuid=True: if True, backends that support either the
         ``UUID`` datatype directly, or a UUID-storing value
         (such as SQL Server's ``UNIQUEIDENTIFIER`` will be used by those
         backends.   If False, a ``CHAR(32)`` datatype will be used for
         all backends regardless of native support.

        """
        self.as_ulid = as_ulid
        self.native_ulid = native_ulid

    @property
    def python_type(self):
        return _python_ULID if self.as_ulid else str

    @property
    def native(self):
        return self.native_ulid

    def coerce_compared_value(self, op, value):
        """See :meth:`.TypeEngine.coerce_compared_value` for a description."""

        if isinstance(value, str):
            return self
        else:
            return super().coerce_compared_value(op, value)

    def bind_processor(self, dialect):
        character_based_ulid = not dialect.supports_native_ulid or not self.native_ulid

        if character_based_ulid:
            if self.as_ulid:

                def process(value):
                    if value is not None:
                        value = value.hex
                    return value

                return process
            else:

                def process(value):
                    if value is not None:
                        value = value.replace("-", "")
                    return value

                return process
        else:
            return None

    def result_processor(self, dialect, coltype):
        character_based_ulid = not dialect.supports_native_ulid or not self.native_ulid

        if character_based_ulid:
            if self.as_ulid:

                def process(value):
                    if value is not None:
                        value = _python_ULID(value)
                    return value

                return process
            else:

                def process(value):
                    if value is not None:
                        value = str(_python_ULID(value))
                    return value

                return process
        else:
            if not self.as_ulid:

                def process(value):
                    if value is not None:
                        value = str(value)
                    return value

                return process
            else:
                return None

    def literal_processor(self, dialect):
        character_based_ulid = not dialect.supports_native_ulid or not self.native_ulid

        if not self.as_ulid:

            def process(value):
                return f"""'{value.replace("-", "").replace("'", "''")}'"""

            return process
        else:
            if character_based_ulid:

                def process(value):
                    return f"""'{value.hex}'"""

                return process
            else:

                def process(value):
                    return f"""'{str(value).replace("'", "''")}'"""

                return process

    def compile(self, dialect=None):
        return "ulid"


class UserDefinedULIDType(_CoerceULIDMixin, UserDefinedType):
    cache_ok = True

    def __init__(self):
        super().__init__()

    def __repr__(self):
        return super().__repr__()

    def get_col_spec(self, **kw):
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


class DifferedULIDType(_CoerceULIDMixin, ScalarCoercible, types.TypeDecorator):
    """
    Stores a ULID in the database as a native column type
    """

    cache_ok = True

    # impl = postgresql.UUID(as_uuid=True)
    # impl = postgresql.CHAR(26)
    # impl = postgresql.BYTEA(16)

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


# ULIDType = UserDefinedULIDType
ULIDType = DifferedULIDType
