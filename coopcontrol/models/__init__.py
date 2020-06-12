# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""Common package methods for coopcontrol.models.

Author: Toni Wells <isometimescode@users.noreply.github.com>

"""

from datetime import datetime

from .. import db


class TimestampMixin():
    """Mixin for adding created and updated timestamps to models."""

    created = db.Column(
        db.Integer,
        nullable=False,
        default=int(datetime.utcnow().timestamp()))
    updated = db.Column(
        db.Integer,
        nullable=False,
        default=int(datetime.utcnow().timestamp()),
        onupdate=int(datetime.utcnow().timestamp()))


class IntEnum(db.TypeDecorator):
    """Special handling of enums as integers instead of strings."""

    impl = db.Integer

    def __init__(self, enumtype, *args, **kwargs):
        super(IntEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, int):
            return value
        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)
