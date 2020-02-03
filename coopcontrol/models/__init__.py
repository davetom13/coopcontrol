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
