# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
Common test fixtures for pytest
"""

import pytest

from coopcontrol import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture(scope="session")
def client(app):
    with app.test_client() as client:
        with app.app_context():
            _db.create_all()
            yield client
            _db.drop_all()


@pytest.fixture(scope="session")
def db_session(client):
    return _db.session


@pytest.fixture()
def cli_runner(app):
    return app.test_cli_runner()
