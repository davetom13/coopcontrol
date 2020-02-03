# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""View methods for the astronomical model.

Author: Toni Wells <isometimescode@users.noreply.github.com>

"""

import click
from flask import Blueprint

from ..models.astronomical import Astronomical, AstroApiHelper

bp = Blueprint("astronomical", __name__, url_prefix="/astronomical")

@bp.route("/<date>")
def get_date(date: str):
    """Get one day's worth of astronomical data from the database."""
    astro = Astronomical()
    result = astro.query.filter_by(date=date).first()
    if result:
        return {"result": result, "status": "OK"}
    return {"result": {}, "status": "NOT_FOUND"}, 404

@bp.cli.command("add-daily")
@click.option("--date", default="today",
              help="An optional date to check, default is today.")
def add_daily(date: str):
    """Add today's astronomical data to the database."""
    astro_helper = AstroApiHelper()
    db_id = astro_helper.add_api_data(date)
    if db_id:
        click.echo(f"Initialized astronomical data for {date}")
    else:
        click.echo(f"Error initializing results for {date}, see logs", err=True)
