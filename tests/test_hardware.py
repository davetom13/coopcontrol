# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
Unit tests for getting/setting hardware data
"""

import pytest

from coopcontrol.models.hardware import Hardware, HardwareStatus

class TestAppplication():
    BLUEPRINT_ROOT="hardware"

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

    # TODO write endpoint tests

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
