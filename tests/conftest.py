# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
Common test fixtures for pytest
"""

import pytest

from coopcontrol import create_app, db

@pytest.fixture(scope="session")
def client():
    app = create_app()
    app.config["TESTING"] = True

    with app.test_client() as client:
        with app.app_context() as ctx:
            db.create_all()
            ctx.push()
            yield client
            db.drop_all()
            ctx.pop()

@pytest.fixture()
def cli_runner(client):
    return client.test_cli_runner()
