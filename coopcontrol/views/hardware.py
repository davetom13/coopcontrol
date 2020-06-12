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


@bp.route("/<name>", methods=["GET"])
def get_hardware(name: str):
    """Get hardware by name."""
    result = Hardware().query.filter(Hardware.name.ilike(name)).first()
    return format_response(result)


@bp.route("/<name>", methods=["PUT", "POST"])
def put_hardware(name: str):
    """Update or create hardware by name."""
    result = Hardware().query.filter(Hardware.name.ilike(name)).first()

    if not result and request.form.get("create") != "true":
        return format_response(
            None, 400, f"{name} not found use create: True to add it.")

    if result:
        model = result
        created = False
        current_app.logger.info(f"Updating existing model {model}")
    else:
        model = Hardware(name=name)
        created = True
        current_app.logger.info(f"Creating new model {model}")

    try:
        for item_name in model.fields():
            item_value = request.form.get(item_name)
            if item_name == "status":
                model.status = HardwareStatus[item_value]
            elif item_value:
                setattr(model, item_name, item_value)
        db.session.add(model)
        db.session.commit()
    except (KeyError, exc.IntegrityError) as e:
        # if the some value provided is invalid
        db.session.rollback()
        return format_response(None, 400, f"Invalid value provided: {e}")
    except exc.SQLAlchemyError as e:
        # some unknown SQLAlchemy error
        current_app.logger.warning(f"Error when updating {name}: {e}")
        db.session.rollback()
        return format_response(None, 500, "Unknown error occurred")

    if created:
        return format_response(model, 201)
    else:
        return format_response(None, 204)


@bp.cli.command("get-hardware-status")
@click.option("--name", required=True, help="A name to check.")
def get_hardware_status(name: str):
    """Get hardware by name."""

    try:
        click.echo(
            Hardware.query.filter(Hardware.name.ilike(name)).one())
    except exc.SQLAlchemyError:
        db.session.rollback()
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
        db.session.rollback()
        click.echo("An unknown error occurred", err=True)
