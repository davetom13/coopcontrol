# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""View methods for the application model.

Author: Toni Wells <isometimescode@users.noreply.github.com>

"""

import click
from flask import Blueprint
from sqlalchemy.orm.exc import NoResultFound

from . import format_response
from ..models.application import Application

bp = Blueprint("application", __name__, url_prefix="/application")

@bp.route("/<name>")
def get_app(name: str):
    """Get application by name."""
    result = Application().query.filter(Application.name.ilike(name)).first()
    return format_response(result)

@bp.cli.command("get-app-status")
@click.option("--name", required=True, help="A name to check.")
def get_app_status(name: str):
    """Get application by name."""

    try:
        click.echo(
            Application.query.filter(Application.name.ilike(name)).one())
    except NoResultFound as e:
        click.echo(f"Not found: {name}", err=True)
