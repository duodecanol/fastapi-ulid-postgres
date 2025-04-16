from __future__ import annotations

from typing import Literal, Optional, TypeVar, overload

from sqlalchemy.sql.type_api import Emulated, TypeEngine
from ulid import ULID as _python_ULID

_ULID_RETURN = TypeVar("_ULID_RETURN", str, _python_ULID)


class Ulid(Emulated, TypeEngine[_ULID_RETURN]):
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
        return "ulid"  # Not working
