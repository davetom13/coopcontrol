# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
Common test fixtures for pytest
"""

import pytest

from coopcontrol import create_app, db as _db

@pytest.fixture(scope="session")
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context():
            _db.create_all()
            yield client
            _db.drop_all()

@pytest.fixture(scope="session")
def db_session(client):
    yield _db.session

@pytest.fixture()
def cli_runner(client):
    return client.test_cli_runner()
