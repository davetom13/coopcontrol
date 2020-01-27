# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
.. module:: astronomical
    :synopsis: `API Data provided by Sunrise-Sunset
          <https://sunrise-sunset.org/api>`_

.. moduleauthor:: Toni Wells <isometimescode@users.noreply.github.com>

"""

import json
import logging
from datetime import datetime

import dataset

from dateutil import parser, tz

from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError

from coopcontrol.configuration import config
from coopcontrol.exception import APIError

class Astronomical:
    """Interact with the sunrise/sunset astronomical data"""

    API_BASE_URL: str="https://api.sunrise-sunset.org/json?%s"
    """
        `API Data provided by Sunrise-Sunset
          <https://sunrise-sunset.org/api>`_
    """

    __raw_data: dict=None
    """The dictionary of data straight from the API"""

    __formatted_data: dict=None
    """
    The dictionary of data formatted for easy display::

        {
            'day_length': 14.29,
            'date_utc': '2015-05-21',
            'sunrise_utc_ts': 1432184735,
            'sunset_utc_ts': 1432236179,
            'date_local': '2015-05-20',
            'sunrise_local_time': '22:05:35-0700',
            'sunset_local_time': '12:22:59-0700'
        }

    """


    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_api_data(self, date: str="today", save: bool=True) -> dict:
        """
        Get the astronomical data for a specific date and
        (optionallly) save it to the database.

        Args:
            date: the astronomical date to check; default to today
            save: true or false, save data to the database; default true

        Returns:
            A dictionary of astronomical data::

                {
                    "day_length'": 12.1
                    ...
                }

        """

        try:
            self.__call_api(
                config.app["latitude"], config.app["longitude"], date)

            self.__format_api_data()

            if (save):
                self.save_record()
            return self.__formatted_data
        except HTTPError as e:
            self.logger.error(f"API error: {e.reason}")
            return None
        except APIError as e:
            self.logger.error(e.message)
            return None

    def save_record(self) -> int:
        """Add or update astronomical data in the database

        Args:
            None

        Returns:
            int: id of new or updated record

        """

        if not self.__formatted_data:
            self.__format_api_data()

        db_data = {
            "date": self.__formatted_data["date_utc"],
            "sunrise": int(self.__formatted_data["sunrise_utc_ts"]),
            "sunset": int(self.__formatted_data["sunset_utc_ts"]),
            "day_length": self.__formatted_data["day_length"],
        }

        self.logger.debug(f"New data: {db_data}")

        db = dataset.connect(config.database["uri"])
        table = db["astronomical"]
        row_id = table.upsert(db_data, ["date"])
        if type(row_id) is int:
            self.logger.info(
                f"New record for date_utc {db_data['date']}: #{row_id}")
            return row_id

        # updates return bool so we have to look for original row
        row_id = table.find_one(date=db_data["date"]).get("id")
        self.logger.info(
            f"Updated record for date_utc {db_data['date']}: #{row_id}")
        return row_id

    def get_record(self, date: str) -> dict:
        """Get astronomical data from the database for a date.

        Args:
            date: the astronomical date to check like "2015-02-14"

        Returns:
            A dictionary of database data. Example::

            {
                'id': 1,
                'day_length': 14.29,
                'date': '2015-05-21',
                'sunrise': 1432184735,
                'sunset': 1432236179,
            }

        Raises:
            ValueError: any errors from parsing the date

        """
        search_date = parser.parse(date).strftime("%Y-%m-%d")

        db = dataset.connect(config.database["uri"])
        table = db["astronomical"]
        row = table.find_one(date=search_date)
        if not row:
            self.logger.debug(f"No records found for {search_date}")
            return None

        # TODO format data
        self.logger.info(f"Found: {row}")
        self.__format_db_data(row)
        return row

    def __call_api(self, latitude: float, longitude: float, date: str) -> None:
        """Get results from sunrise JSON API

        Args:
            latitude: latitude to query. Example:: 12.12345
            longitude: longitude to query. Example:: -123.12345
            date: the astronomical date to query. Examples::

                - 2016-01-01
                - today

        Returns:
            None

        Raises:
            urllib.HTTPError: any errors from calling the API

        Note:
            __raw_results will be set to the results from the API::

                {
                  'sunrise': '2016-02-23T15:00:16+00:00',
                  'sunset': '2016-02-24T01:44:50+00:00',
                  'solar_noon': '2016-02-23T20:22:33+00:00',
                  'day_length': 38674,
                  'civil_twilight_begin': '2016-02-23T14:29:08+00:00',
                  'civil_twilight_end': '2016-02-24T02:15:58+00:00',
                  'nautical_twilight_begin': '2016-02-23T13:53:21+00:00',
                  'nautical_twilight_end': '2016-02-24T02:51:44+00:00',
                  'astronomical_twilight_begin': '2016-02-23T13:17:39+00:00',
                  'astronomical_twilight_end': '2016-02-24T03:27:26+00:00'
                }

        """

        args = {
            "date": date,
            "lat": latitude,
            "lng": longitude,
            "formatted": 0,
        }
        url = self.API_BASE_URL % urlencode(args)
        self.logger.info(f"Calling API with {url}")

        with urlopen(url) as resource:
            response = json.load(resource)
            if "results" not in response or response.get("status") != "OK":
                self.logger.info(f"API Raw Response {response}")
                raise APIError(
                    "Sunrise-Sunset API", "Malformed response, missing results")
            self.logger.debug(f"API Raw Response {response}")
            self.__raw_data = response["results"]

    def __format_db_data(self, record: dict) -> None:
        """Convert a db row record into a timezone-appropriate format

        Args:
            record: A database dictionary record to format

        Returns:
            None

        Note:
            Updates a private var with formatted data. See documentation
            for __formatted_data for a list of keys.

        """

        utc_sr = datetime.fromtimestamp(record["sunrise"])
        sunrise_local_time = utc_sr.astimezone(tz.gettz(config.app["timezone"]))

        utc_ss = datetime.fromtimestamp(record["sunset"])
        sunset_local_time = utc_ss.astimezone(tz.gettz(config.app["timezone"]))

        self.__formatted_data = {
            "day_length": record["day_length"],

            "date_utc": record["date"],
            "sunrise_utc_ts": record["sunrise"],
            "sunset_utc_ts": record["sunset"],

            "date_local": sunrise_local_time.strftime("%Y-%m-%d"),
            "sunrise_local_time": sunrise_local_time.strftime("%H:%M:%S%z"),
            "sunset_local_time": sunset_local_time.strftime("%H:%M:%S%z"),
        }

    def __format_api_data(self) -> None:
        """Convert API data into a timezone-appropriate format

        Args:
            None

        Returns:
            None

        Raises:
            ValueError: when data is missing

        Note:
            Updates a private var with formatted data. See documentation
            for __formatted_data for a list of keys.

        """

        if not self.__raw_data:
            raise ValueError("Cannot format data: raw_data not found")

        # the api results look like 2015-12-10T15:47:11+00:00
        utc_sr = parser.parse(self.__raw_data["sunrise"])
        sunrise_local_time = utc_sr.astimezone(tz.gettz(config.app["timezone"]))

        utc_ss = parser.parse(self.__raw_data["sunset"])
        sunset_local_time = utc_ss.astimezone(tz.gettz(config.app["timezone"]))

        self.__formatted_data = {
            # day is stored in seconds and exact precision is not necessary
            "day_length": round(self.__raw_data["day_length"] / 60 / 60, 2),

            "date_utc": utc_sr.strftime("%Y-%m-%d"),
            "sunrise_utc_ts": utc_sr.timestamp(),
            "sunset_utc_ts": utc_ss.timestamp(),

            "date_local": sunrise_local_time.strftime("%Y-%m-%d"),
            "sunrise_local_time": sunrise_local_time.strftime("%H:%M:%S%z"),
            "sunset_local_time": sunset_local_time.strftime("%H:%M:%S%z"),
        }
