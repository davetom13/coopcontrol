# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""Common package methods for coopcontrol.

Author: Toni Wells <isometimescode@users.noreply.github.com>

"""

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy

from .configuration import config

db = SQLAlchemy()
"""Global DB instance."""

def create_app():
    """Flask factory method.

    Args:
        None

    Returns:
        Flask: instance of Flask app

    """
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=config.flask["secret_key"],
        SQLALCHEMY_DATABASE_URI=config.database["uri"],
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    db.init_app(app)

    # import all the blueprints we need
    from .views import astronomical, application, hardware
    app.register_blueprint(views.astronomical.bp)
    app.register_blueprint(views.application.bp)
    app.register_blueprint(views.hardware.bp)

    return app
