# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
Model for getting general application data.

Author: Toni Wells <isometimescode@users.noreply.github.com>

"""

import enum
from dataclasses import dataclass

from . import TimestampMixin, IntEnum
from .. import db


class AppStatus(enum.IntEnum):
    ACTIVE: int = 1
    """An application is active and usable."""

    LOCKED: int = 2
    """An application is temporarily unusable."""

    ARCHIVED: int = 3
    """An application is permanently unusable or inactive."""


@dataclass
class Application(TimestampMixin, db.Model):
    """DB model for holding application data."""

    id: int = db.Column(db.Integer, primary_key=True)
    """Primary identifier."""

    name: str = db.Column(db.String, unique=True)
    """Unique application name, should be the same as config.app.name."""

    status: int = db.Column(
        IntEnum(AppStatus), default=AppStatus.ACTIVE, nullable=False)
    """Whether an application is active or not."""
