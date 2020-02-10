# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
Unit tests for getting/setting application data
"""

import pytest

import coopcontrol.models.application

class TestAppplication():
    @pytest.fixture()
    def app_test_row(self, db_session):
        # check if duplicate exists
        name = "MyCoolApp"
        model = db_session.query(coopcontrol.models.application.Application) \
            .filter_by(name=name).first()

        if model:
            return model

        # no duplicate found, insert this one
        model = coopcontrol.models.application.Application(name=name)

        db_session.add(model)
        db_session.commit()
        return model

    def test_endpoint_get_app_success(self, client, app_test_row):
        """Get a basic application record from the db."""
        rv = client.get("/application/MyCoolApp")
        data = rv.get_json()
        assert data.get("status") == "OK"
        assert {"id", "name", "status"} >= data["result"].keys()
        assert data["result"]["name"] == "MyCoolApp"

    def test_endpoint_get_app_caseinsensitive_search(self, client, app_test_row):
        """Get a record even if the capitalization is different."""
        rv = client.get("/application/mycoolapp")
        data = rv.get_json()
        assert data.get("status") == "OK"
        assert {"id", "name", "status"} >= data["result"].keys()
        assert data["result"]["name"] == "MyCoolApp"

    def test_endpoint_get_app_notfound(self, client):
        """Get a record that does not exist."""
        rv = client.get("/application/not_an_app_name")
        data = rv.get_json()
        assert data.get("status") == "NOT_FOUND"
        assert data["result"] == dict()
