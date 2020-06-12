# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
Model for getting general hardware data.

Author: Toni Wells <isometimescode@users.noreply.github.com>

"""

import logging
import enum
from dataclasses import dataclass, asdict

from . import TimestampMixin, IntEnum
from .. import db

class HardwareStatus(enum.IntEnum):
    OPEN: int = 1
    """A piece of hardware is open or on."""

    CLOSED: int = 2
    """A piece of hardware is closed or off."""

    DISABLED: int = 3
    """A piece of hardware is not in use."""

@dataclass
class Hardware(TimestampMixin, db.Model):
    """DB model for holding hardware data."""

    id: int = db.Column(db.Integer, primary_key=True)
    """Primary identifier."""

    name: str = db.Column(db.String, unique=True)
    """
        Unique hardware name, which can (optionally)
        be mapped to a hardware model type.
    """

    app_id: int = db.Column(db.Integer, nullable=False)
    """Foreign key to the application table."""

    bcm_pin_write: int = db.Column(db.Integer, nullable=False)
    """The BCM pin to use when writing values to control board."""

    bcm_pin_read: int = db.Column(db.Integer, nullable=False)
    """The BCM pin to use when reading values from the control board."""

    status: int = db.Column(
        IntEnum(HardwareStatus), default=HardwareStatus.DISABLED, nullable=False)
    """The current state of the piece of hardware."""

    def fields(self):
        """Get a set of all fields for this model.

        Arguments:
            None

        Returns:
            Set of fields for this model
        """
        return set(asdict(self).keys())
