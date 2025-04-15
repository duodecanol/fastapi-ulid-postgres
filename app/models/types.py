from __future__ import absolute_import

import uuid

import ulid
from sqlalchemy import types, util
from sqlalchemy.dialects import postgresql
from sqlalchemy_utils.types.scalar_coercible import ScalarCoercible
from ulid import ULID


class ULIDType(types.TypeDecorator, ScalarCoercible):
    """
    Stores a ULID in the database as a native UUID column type
    but can use TEXT if needed.
    ::
        from .lib.sqlalchemy_types import ULIDType
        class User(Base):
            __tablename__ = 'user'
            # Pass `force_text=True` to fallback TEXT instead of UUID column
            id = sa.Column(ULIDType(force_text=False), primary_key=True)
    """

    cache_ok = True

    impl = postgresql.UUID(as_uuid=True)

    python_type = ulid.ULID

    def __init__(self, force_text=False, **kwargs):
        """
        :param force_text: Store ULID as TEXT instead of UUID.
        """
        self.force_text = force_text

    def __repr__(self):
        return util.generic_repr(self)

    def load_dialect_impl(self, dialect):
        if self.force_text:
            return dialect.type_descriptor(types.UnicodeText)

        return dialect.type_descriptor(self.impl)

    @staticmethod
    def _coerce(value):
        if not value:
            return None

        if isinstance(value, str):
            try:
                value = ulid.ULID.from_str(value)
            except (TypeError, ValueError):
                value = ulid.ULID.from_hex(value)

            return value

        if isinstance(value, uuid.UUID):
            return ulid.ULID.from_bytes(value.bytes)

        if not isinstance(value, ULID):
            return ulid.ULID.from_bytes(value)

        return value

    def process_bind_param(self, value, dialect):
        if value is None:
            return value

        if not isinstance(value, ulid.ULID):
            value = self._coerce(value)

        return str(value.to_uuid())

    def process_result_value(self, value, dialect):
        if value is None:
            return value

        return self._coerce(value)
