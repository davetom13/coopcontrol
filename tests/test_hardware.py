# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
Unit tests for getting/setting hardware data
"""

import pytest

from coopcontrol.models.hardware import Hardware, HardwareStatus

class TestAppplication():
    BLUEPRINT_ROOT="hardware"
    FIELD_LIST = Hardware().fields()

    @pytest.fixture()
    def hardware_test_row(self, db_session):
        # check if duplicate exists
        name = "TestLight"
        model = db_session.query(Hardware).filter_by(name=name).first()

        if model:
            return model

        # no duplicate found, insert this one
        model = Hardware(name=name, bcm_pin_write=35, bcm_pin_read=35, app_id=1)

        db_session.add(model)
        db_session.commit()
        return model

    def test_endpoint_get_hardware_success(self, client, hardware_test_row):
        """Get a basic hardware record from the db."""
        rv = client.get(f"/{self.BLUEPRINT_ROOT}/TestLight")
        data = rv.get_json()
        assert rv.status_code == 200
        assert self.FIELD_LIST == data["result"].keys()
        assert data["status"] == "OK"
        assert data["result"]["name"] == "TestLight"

    def test_endpoint_get_hardware_caseinsensitive_search(self, client, hardware_test_row):
        """Get a record even if the capitalization is different."""
        rv = client.get(f"/{self.BLUEPRINT_ROOT}/testlight")
        data = rv.get_json()
        assert data["result"]["name"] == "TestLight"

    def test_endpoint_get_hardware_notfound(self, client):
        """Get a record that does not exist."""
        rv = client.get(f"/{self.BLUEPRINT_ROOT}/not_a_hardware_name")
        data = rv.get_json()
        assert rv.status_code == 404
        assert data["status"] == "NOT_FOUND"
        assert data["result"] == dict()

    def test_endpoint_post_hardware_success_create(self, client):
        """Create a new piece of hardware."""
        rv = client.post(f"/{self.BLUEPRINT_ROOT}/NewTestLight", data={
            "status":HardwareStatus.OPEN.name,
            "app_id":1,
            "bcm_pin_write": 4,
            "bcm_pin_read": 4,
            "create":"true",
            })
        data = rv.get_json()
        assert rv.status_code == 201
        assert self.FIELD_LIST == data["result"].keys()
        assert data["status"] == "OK"
        assert data["result"]["name"] == "NewTestLight"

    def test_endpoint_post_hardware_success_update(self, client, hardware_test_row):
        """Create a new piece of hardware."""
        rv = client.post(f"/{self.BLUEPRINT_ROOT}/testlight", data={
            "status":HardwareStatus.CLOSED.name,
            })
        assert rv.status_code == 204

    def test_endpoint_post_hardware_create_required(self, client):
        """See an error when we don't send a create param but the model is new."""
        rv = client.put(f"/{self.BLUEPRINT_ROOT}/testlight_withcreate", data={
            "create": "false"})
        data = rv.get_json()
        assert rv.status_code == 400
        assert data["status"] == "ERROR"
        assert data["result"] == dict()
        assert "not found use create" in data["message"].lower()

    def test_endpoint_post_hardware_invalid_value(self, client):
        """See an error when invalid status."""
        rv = client.put(f"/{self.BLUEPRINT_ROOT}/testlight_invalid", data={
            "status":"NOT_A_REAL_STATUS", "create": "true"})
        data = rv.get_json()
        assert rv.status_code == 400
        assert data["status"] == "ERROR"
        assert data["result"] == dict()
        assert "not_a_real_status" in data["message"].lower()

    def test_endpoint_post_hardware_error_nodata(self, client, hardware_test_row):
        """See an error when missing data to update."""
        rv = client.put(f"/{self.BLUEPRINT_ROOT}/testlight", data={})
        data = rv.get_json()
        assert rv.status_code == 400
        assert data["status"] == "ERROR"
        assert data["result"] == dict()
        assert "none" in data["message"].lower()

    def test_endpoint_post_hardware_error_missing_field(self, client):
        """See an error when missing a required field."""
        rv = client.put(f"/{self.BLUEPRINT_ROOT}/testlight_missing", data={
            "status":HardwareStatus.CLOSED.name,
            "bcm_pin_read": 12,
            "create":"true",
            })
        data = rv.get_json()
        assert rv.status_code == 400
        assert data["status"] == "ERROR"
        assert data["result"] == dict()
        assert "none" in data["message"].lower()

    def test_cli_get_hardware_success(self, cli_runner, hardware_test_row):
        result = cli_runner.invoke(args=[
            self.BLUEPRINT_ROOT, "get-hardware-status",
            "--name", hardware_test_row.name.lower()])
        assert hardware_test_row.name in result.output

    def test_cli_get_hardware_missing(self, cli_runner):
        result = cli_runner.invoke(args=[
            self.BLUEPRINT_ROOT, "get-hardware-status",
            "--name", "missinghardware"])
        assert "Not found" in result.output

    def test_cli_set_hardware_success(self, cli_runner, hardware_test_row):
        result = cli_runner.invoke(args=[
            self.BLUEPRINT_ROOT, "set-hardware-status",
            "--name", hardware_test_row.name,
            "--status", "OPEN"])
        assert hardware_test_row.name in result.output
        assert "OPEN" in result.output

    def test_cli_set_hardware_error_missing_update(self, cli_runner):
        result = cli_runner.invoke(args=[
            self.BLUEPRINT_ROOT, "set-hardware-status",
            "--name", "SomeMissingHardware",
            "--status", "OPEN"])
        assert "not found" in result.output
