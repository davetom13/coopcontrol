# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
Unit tests for getting/setting application data
"""

import pytest

from coopcontrol.models.application import Application, AppStatus

class TestAppplication():
    BLUEPRINT_ROOT="application"

    @pytest.fixture()
    def app_test_row(self, db_session):
        # check if duplicate exists
        name = "MyCoolApp"
        model = db_session.query(Application).filter_by(name=name).first()

        if model:
            return model

        # no duplicate found, insert this one
        model = Application(name=name)

        db_session.add(model)
        db_session.commit()
        return model

    def test_endpoint_get_app_success(self, client, app_test_row):
        """Get a basic application record from the db."""
        rv = client.get(f"/{self.BLUEPRINT_ROOT}/MyCoolApp")
        data = rv.get_json()
        assert rv.status_code == 200
        assert {"id", "name", "status"} == data["result"].keys()
        assert data["status"] == "OK"
        assert data["result"]["name"] == "MyCoolApp"

    def test_endpoint_get_app_caseinsensitive_search(self, client, app_test_row):
        """Get a record even if the capitalization is different."""
        rv = client.get(f"/{self.BLUEPRINT_ROOT}/mycoolapp")
        data = rv.get_json()
        assert data["result"]["name"] == "MyCoolApp"

    def test_endpoint_get_app_notfound(self, client):
        """Get a record that does not exist."""
        rv = client.get(f"/{self.BLUEPRINT_ROOT}/not_an_app_name")
        data = rv.get_json()
        assert rv.status_code == 404
        assert data["status"] == "NOT_FOUND"
        assert data["result"] == dict()

    def test_endpoint_post_app_status_success(self, client):
        """Update an app's status successfully."""
        rv = client.put(f"/{self.BLUEPRINT_ROOT}/mycoolapp", data={
            "status":AppStatus.LOCKED.name})
        assert rv.status_code == 204

    def test_endpoint_post_app_status_invalid(self, client):
        """See an error when invalid status update."""
        rv = client.put(f"/{self.BLUEPRINT_ROOT}/mycoolapp", data={
            "status":"NOT_A_REAL_STATUS"})
        data = rv.get_json()
        assert rv.status_code == 400
        assert data["status"] == "ERROR"
        assert data["result"] == dict()
        assert "invalid appstatus" in data["message"].lower()

    def test_endpoint_post_app_status_required(self, client):
        """See an error when missing status update."""
        rv = client.put(f"/{self.BLUEPRINT_ROOT}/mycoolapp", data={})
        data = rv.get_json()
        assert rv.status_code == 400
        assert data["status"] == "ERROR"
        assert data["result"] == dict()
        assert "missing status" in data["message"].lower()

    def test_cli_get_app_success(self, cli_runner, app_test_row):
        result = cli_runner.invoke(args=[
            self.BLUEPRINT_ROOT, "get-app-status",
            "--name", app_test_row.name.lower()])
        assert app_test_row.name in result.output

    def test_cli_get_app_missing(self, cli_runner):
        result = cli_runner.invoke(args=[
            self.BLUEPRINT_ROOT, "get-app-status",
            "--name", "missingapp"])
        assert "Not found" in result.output

    def test_cli_set_app_success_create(self, cli_runner):
        result = cli_runner.invoke(args=[
            self.BLUEPRINT_ROOT, "set-app-status",
            "--name", "MyCLIApp",
            "--status", "ACTIVE",
            "--create"])
        assert "MyCLIApp" in result.output
        assert "ACTIVE" in result.output

    def test_cli_set_app_success_update(self, cli_runner, app_test_row):
        result = cli_runner.invoke(args=[
            self.BLUEPRINT_ROOT, "set-app-status",
            "--name", app_test_row.name,
            "--status", "ARCHIVED",
            "--no-create"])
        assert app_test_row.name in result.output
        assert "ARCHIVED" in result.output

    def test_cli_set_app_error_duplicate_create(self, cli_runner, app_test_row):
        result = cli_runner.invoke(args=[
            self.BLUEPRINT_ROOT, "set-app-status",
            "--name", app_test_row.name,
            "--status", "LOCKED",
            "--create"])
        assert "already exists" in result.output

    def test_cli_set_app_error_missing_update(self, cli_runner):
        result = cli_runner.invoke(args=[
            self.BLUEPRINT_ROOT, "set-app-status",
            "--name", "SomeMissingApp",
            "--status", "LOCKED",
            "--no-create"])
        assert "not found" in result.output
