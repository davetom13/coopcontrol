# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
Unit tests for getting/setting astronomical data
"""

import pytest
from unittest.mock import MagicMock
from urllib.error import HTTPError

import coopcontrol.models.astronomical

class TestAstroApiHelper():
    # Expected result for a good API request
    JSON_SUCCESS = '''
        {
          "results":
          {
            "sunrise":"2015-05-21T05:05:35+00:00",
            "sunset":"2015-05-21T19:22:59+00:00",
            "solar_noon":"2015-05-21T12:14:17+00:00",
            "day_length":51444,
            "civil_twilight_begin":"2015-05-21T04:36:17+00:00",
            "civil_twilight_end":"2015-05-21T19:52:17+00:00",
            "nautical_twilight_begin":"2015-05-21T04:00:13+00:00",
            "nautical_twilight_end":"2015-05-21T20:28:21+00:00",
            "astronomical_twilight_begin":"2015-05-21T03:20:49+00:00",
            "astronomical_twilight_end":"2015-05-21T21:07:45+00:00"
          },
           "status":"OK"
        }
        '''

    # Exepected result when bad params are set to the API
    JSON_FAILURE = '''{"results":"","status":"INVALID_REQUEST"}'''

    def __get_resp_mock(self, code, ret):
        """Get a mock object with response and code."""
        respmock = MagicMock()
        respmock.getcode.return_value = code
        respmock.read.return_value = ret
        respmock.__enter__.return_value = respmock
        respmock.return_value = respmock
        return respmock

    @pytest.fixture()
    def astro(self, client):
        return coopcontrol.models.astronomical.AstroApiHelper()

    @pytest.fixture()
    def mock_urlopen_success(self, monkeypatch):
        respmock = self.__get_resp_mock(200, self.JSON_SUCCESS)
        monkeypatch.setattr(coopcontrol.models.astronomical, "urlopen", respmock)
        return respmock

    @pytest.fixture()
    def mock_urlopen_fail(self, monkeypatch):
        respmock = self.__get_resp_mock(400, self.JSON_FAILURE)
        monkeypatch.setattr(coopcontrol.models.astronomical, "urlopen", respmock)
        return respmock

    def test_api_success(self, astro, mock_urlopen_success):
        """Normal request with no problems."""
        result_id = astro.add_api_data()
        assert result_id >= 1

    def test_api_success_with_duplicate(self, astro, mock_urlopen_success):
        """No errors when inserting duplicate dates."""
        first_result_id = astro.add_api_data()
        assert first_result_id >= 1

        next_result_id = astro.add_api_data()
        assert next_result_id == first_result_id

    def test_api_fail_http_status(self, astro, mock_urlopen_fail):
        """Raises an exception in the request."""
        mock_urlopen_fail.side_effect = HTTPError(
            None, None, "Mocked Side Effect", None, None)
        response = astro.add_api_data()
        assert response == None

    def test_api_fail_malformed_response(self, astro, mock_urlopen_fail):
        """No exception but return bad JSON."""
        response = astro.add_api_data()
        assert response == None

    def test_get_record_success(self, client):
        """Get a basic astronomical record from the db."""
        rv = client.get("/astronomical/2015-05-21")
        data = rv.get_json()
        assert data.get("status") == "OK"
        assert data["result"]["date"] == "2015-05-21"

    def test_get_record_notfound(self, client):
        """Get a record that does not exist."""
        rv = client.get("/astronomical/1970-01-01")
        data = rv.get_json()
        assert data.get("status") == "NOT_FOUND"
        assert data["result"] == dict()
