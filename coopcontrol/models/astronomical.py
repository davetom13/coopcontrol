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
from dataclasses import dataclass
import datetime

from dateutil import parser, tz

from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError

from . import TimestampMixin
from .. import config, db
from ..exception import APIError


@dataclass
class Astronomical(TimestampMixin, db.Model):
    """DB model for holding astronomical data."""

    DATE_FORMAT: str = "%Y-%m-%d"
    """strftime format string for a date."""

    TIME_FORMAT: str = "%H:%M:%S%z"
    """stftime format string for a time."""

    id: int = db.Column(db.Integer, primary_key=True)
    date: datetime.date = db.Column(db.Date, unique=True)
    sunrise: int = db.Column(db.Integer, nullable=False)
    sunset: int = db.Column(db.Integer, nullable=False)
    day_length: int = db.Column(db.Integer, nullable=False)

    def get_with_local(self):
        """Convert all data to the config timezone.

        Args:
            None

        Returns:
            dict: all of the models data plus time zone info. Example::

            {
                "id": 1,
                "date": "2020-02-08",
                "date_local": "2020-02-08",
                "day_length": 9,
                "sunrise": "15:25:28+0000",
                "sunrise_local": "07:25:28-0800",
                "sunset": "01:21:23+0000",
                "sunset_local": "17:21:23-0800"
            }

        Raises:
            ValueError: when data is missing

        """
        if not self.date:
            raise ValueError("No data found to convert")

        newdate = parser.parse(str(self.date))
        sr = datetime.datetime.fromtimestamp(self.sunrise, tz.UTC)
        ss = datetime.datetime.fromtimestamp(self.sunset, tz.UTC)

        result = {
            "id": self.id,
            "date": newdate.strftime(self.DATE_FORMAT),
            "sunrise": sr.strftime(self.TIME_FORMAT),
            "sunset": ss.strftime(self.TIME_FORMAT),
            "day_length": self.day_length,
        }

        # convert to the config tz
        localtz = tz.gettz(config.app["timezone"])
        newdate = newdate.astimezone(localtz)
        sr = sr.astimezone(localtz)
        ss = ss.astimezone(localtz)

        result["date_local"] = newdate.strftime(self.DATE_FORMAT)
        result["sunrise_local"] = sr.strftime(self.TIME_FORMAT)
        result["sunset_local"] = ss.strftime(self.TIME_FORMAT)

        return result


class AstroApiHelper():
    """Interact with the sunrise/sunset astronomical data"""

    API_BASE_URL: str = "https://api.sunrise-sunset.org/json?%s"
    """
        `API Data provided by Sunrise-Sunset
          <https://sunrise-sunset.org/api>`_
    """

    __raw_data: dict = None
    """The dictionary of data straight from the API"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def add_api_data(self, date: str = "today") -> int:
        """
        Get the astronomical data for a specific date and
        save it to the database.

        Args:
            date: the astronomical date to check; default to today

        Returns:
            integer: database id of row added

        """

        try:
            self.__call_api(
                config.app["latitude"], config.app["longitude"], date)
            return self.__save_record()
        except HTTPError as e:
            self.logger.error(f"API error: {e.reason}")
            return None
        except APIError as e:
            self.logger.error(e.message)
            return None

    def __save_record(self) -> int:
        """Add or update astronomical data in the database

        Args:
            None

        Returns:
            int: id of new or duplicate record

        Raises:
            ValueError: when data is missing

        """

        if not self.__raw_data:
            raise ValueError("Cannot save data: raw_data not found")

        # the api results look like 2015-12-10T15:47:11+00:00
        utc_sr = parser.parse(self.__raw_data["sunrise"])
        utc_ss = parser.parse(self.__raw_data["sunset"])

        db_data = {
            "date": utc_sr,
            "sunrise": utc_sr.timestamp(),
            "sunset": utc_ss.timestamp(),

            # day is stored in seconds and exact precision is not necessary
            "day_length": int(self.__raw_data["day_length"] / 60 / 60),
        }

        self.logger.debug(f"db_data: {db_data}")

        # first check if this data exists; not race-condition safe
        astro = Astronomical.query.filter_by(
            date=db_data['date'].date()).first()
        if astro:
            self.logger.info(
                f"Skipping insert for existing record date_utc "
                f"{db_data['date']}: #{astro.id}")
            return astro.id

        # no duplicate found, insert a new one
        astro = Astronomical(**db_data)
        db.session.add(astro)
        db.session.commit()

        self.logger.info(
            f"New record for date_utc {db_data['date']}: #{astro.id}")
        return astro.id

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
        self.logger.debug(f"Calling API with {url}")

        with urlopen(url) as resource:
            response = json.load(resource)
            if "results" not in response or response.get("status") != "OK":
                self.logger.info(f"API Raw Response {response}")
                raise APIError(
                    "Sunrise-Sunset API",
                    "Malformed response, missing results")
            self.logger.debug(f"API Raw Response {response}")
            self.__raw_data = response["results"]
