# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
Unit tests for getting/setting astronomical data
"""

import unittest
from unittest.mock import patch, MagicMock
from urllib.error import HTTPError

from coopcontrol.astronomical import Astronomical

class TestAstronomical(unittest.TestCase):
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

    def setUp(self):
        self.astro = Astronomical()

    def tearDown(self):
        self.astro = None

    def get_resp_mock(self, code, ret):
        respmock = MagicMock()
        respmock.getcode.return_value = code
        respmock.read.return_value = ret
        respmock.__enter__.return_value = respmock
        return respmock

    @patch('coopcontrol.astronomical.urlopen')
    def test_api_success_withdb(self, mock_urlopen):
        mock_urlopen.return_value = self.get_resp_mock(200, self.JSON_SUCCESS)
        response = self.astro.get_api_data("today", True)
        self.assertIn("sunrise_local_time", response)
        self.assertIn("sunset_local_time", response)
        self.assertIn("day_length", response)
        self.assertGreaterEqual(response.get("db_id"), 1)

    @patch('coopcontrol.astronomical.urlopen')
    def test_api_success_withoutdb(self, mock_urlopen):
        mock_urlopen.return_value = self.get_resp_mock(200, self.JSON_SUCCESS)
        response = self.astro.get_api_data("today", False)
        self.assertIn("sunrise_local_time", response)
        self.assertIn("sunset_local_time", response)
        self.assertIn("day_length", response)
        self.assertIsNone(response["db_id"])

    @patch('coopcontrol.astronomical.urlopen')
    def test_api_fail_http_status(self, mock_urlopen):
        mock_urlopen.return_value = self.get_resp_mock(400, self.JSON_FAILURE)
        mock_urlopen.side_effect = HTTPError(*[None] * 5)
        response = self.astro.get_api_data()
        self.assertIsNone(response)

    @patch('coopcontrol.astronomical.urlopen')
    def test_api_fail_malformed_response(self, mock_urlopen):
        mock_urlopen.return_value = self.get_resp_mock(400, self.JSON_FAILURE)
        response = self.astro.get_api_data()
        self.assertIsNone(response)

    @patch('coopcontrol.astronomical.urlopen')
    def test_save_record_success(self, mock_urlopen):
        # first load data to private vars
        mock_urlopen.return_value = self.get_resp_mock(200, self.JSON_SUCCESS)
        self.astro.get_api_data("today", False)

        # actual test with saving to db
        id = self.astro.save_record()
        self.assertIs(type(id), int)
        self.assertGreaterEqual(id, 1)

    def test_save_record_missing_data(self):
        # fails because data isn't loaded in vars
        with self.assertRaises(ValueError):
            self.astro.save_record()

    def test_get_record_success(self):
        # first make sure there is a record in the test db
        self.test_save_record_success()

        for date in {"2015-05-21", "May 21, 2015", "2015-05-21T05:05:35+00:00"}:
            with self.subTest(date=date):
                record = self.astro.get_record(date)
                self.assertIn("id", record)
                self.assertEqual("2015-05-21", record.get("date"))

    def test_get_record_not_found(self):
        record = self.astro.get_record("1970-01-01")
        self.assertIsNone(record)

    def test_get_record_bad_date(self):
        with self.assertRaises(ValueError):
            self.astro.get_record("foo")

if __name__ == "__main__":
    unittest.main()
