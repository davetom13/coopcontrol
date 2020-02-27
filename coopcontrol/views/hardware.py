# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""View methods for the hardware models.

Author: Toni Wells <isometimescode@users.noreply.github.com>

"""

import click
from flask import Blueprint, request, current_app
from sqlalchemy import exc

from . import format_response
from ..models.hardware import Hardware, HardwareStatus
from .. import db

bp = Blueprint("hardware", __name__, url_prefix="/hardware")

# TODO add REST API endpoints

@bp.cli.command("get-hardware-status")
@click.option("--name", required=True, help="A name to check.")
def get_hardware_status(name: str):
    """Get hardware by name."""

    try:
        click.echo(
            Hardware.query.filter(Hardware.name.ilike(name)).one())
    except exc.SQLAlchemyError as e:
        click.echo(f"Not found: {name}", err=True)

@bp.cli.command("set-hardware-status")
@click.option("--name", required=True, help="A name for the hardware.")
@click.option(
    "--status", required=True,
    type=click.Choice([s.name for s in HardwareStatus]),
    help="A status for the piece of hardware.")
def set_hardware_status(name: str, status: str):
    """Update the status for a piece of hardware."""

    if not name:
        click.echo("name is required", err=True)
        return

    item = Hardware.query.filter(Hardware.name.ilike(name)).first()
    if not item:
        click.echo(f"{name} not found, cannot update status", err=True)
        return

    try:
        item.status = HardwareStatus[status]
        db.session.add(item)
        db.session.commit()
        click.echo(f"Updated Hardware: {item}")
    except exc.SQLAlchemyError as e:
        # some unknown SQLAlchemy error
        current_app.logger.warning(f"Error when updating {name}: {e}")
        click.echo(f"An unknown error occurred", err=True)
