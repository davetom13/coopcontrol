# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""View methods for the application model.

Author: Toni Wells <isometimescode@users.noreply.github.com>

"""

import click
from flask import Blueprint, request, current_app
from sqlalchemy import exc

from . import format_response
from ..models.application import Application, AppStatus
from .. import db

bp = Blueprint("application", __name__, url_prefix="/application")

@bp.route("/<name>", methods=["GET", "PUT", "POST"])
def get_app(name: str):
    """Get application by name."""
    result = Application().query.filter(Application.name.ilike(name)).first()
    if not result or request.method == "GET":
        return format_response(result)

    # it's an update (PUT, POST)
    if "status" not in request.form:
        return format_response(None, 400, "Missing status in update")

    try:
        result.status = AppStatus[request.form["status"]]
        db.session.add(result)
        db.session.commit()
    except KeyError as e:
        # if the AppStatus provided is invalid
        return format_response(None, 400, "Invalid AppStatus provided")
    except exc.SQLAlchemyError as e:
        # some unknown SQLAlchemy error
        current_app.logger.warning(f"Error when updating {name}: {e}")
        return format_response(None, 500, "Unknown error occurred")

    # otherwise all is well
    return format_response(None, 204)

@bp.cli.command("get-app-status")
@click.option("--name", required=True, help="A name to check.")
def get_app_status(name: str):
    """Get application by name."""

    try:
        click.echo(
            Application.query.filter(Application.name.ilike(name)).one())
    except exc.SQLAlchemyError as e:
        click.echo(f"Not found: {name}", err=True)

@bp.cli.command("set-app-status")
@click.option("--name", required=True, help="A name for the application.")
@click.option("--status", required=True, type=click.Choice([s.name for s in AppStatus]),
    help="A status for the application.")
@click.option("--create/--no-create", default=False,
    help="Create a new app if a matching name is not found. (default: false)")
def set_app_status(name: str, status: str, create: bool):
    """Create a new application."""

    if not name:
        click.echo("name is required", err=True)
        return

    app = Application.query.filter(Application.name.ilike(name)).first()
    if create:
        if app:
            click.echo(f"{name} already exists, use --no-create to modify it", err=True)
            return
        else:
            app = Application(name=name)
    elif not app:
        click.echo(f"{name} not found, use --create to add it", err=True)
        return

    try:
        app.status = AppStatus[status]
        db.session.add(app)
        db.session.commit()
        click.echo(f"Set Application: {app}")
    except exc.SQLAlchemyError as e:
        # some unknown SQLAlchemy error
        current_app.logger.warning(f"Error when creating {name}: {e}")
        click.echo(f"An unknown error occurred", err=True)
