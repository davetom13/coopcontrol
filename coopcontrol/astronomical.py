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

from dateutil import parser, tz

from urllib.request import urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError

from coopcontrol.configuration import config
from coopcontrol.exception import APIError

class Astronomical:
    """Interact with the sunrise/sunset astronomical data"""

    API_BASE_URL = "https://api.sunrise-sunset.org/json?%s"
    """
        `API Data provided by Sunrise-Sunset
          <https://sunrise-sunset.org/api>`_
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def get_api_data(self,
        astronomical_date: str="today", save: bool=True) -> dict:
        """
        Get the astronomical data for a specific date and
        (optionallly) save it to the database.

        Args:
            astronomical_date: the date to check; default to today
            save: true or false, save data to the database; default true

        Returns:
            A dictionary of astronomical data::

                {
                    "day_length'": 12.1
                    ...
                }

        """

        try:
            api_data = self.__call_api(
                    config.app["latitude"], config.app["longitude"],
                    astronomical_date)

            if (save):
                self.__set_local_data(api_data)
            return api_data
        except HTTPError as e:
            self.logger.error(f"API error: {e.reason}")
            return None
        except APIError as e:
            self.logger.error(e.message)
            return None

    def __call_api(self,
        latitude: float, longitude: float, astronomical_date: str) -> dict:
        """Get results from sunrise JSON API

        Args:
            latitude: latitude to query. Example:: 12.12345
            longitude: longitude to query. Example:: -123.12345
            astronomical_date: the date to query. Examples::

                - 2016-01-01
                - today

        Returns:
            A dictionary of the results from the API::

                {
                  "sunrise": "2016-02-23T15:00:16+00:00",
                  "sunset": "2016-02-24T01:44:50+00:00",
                  "solar_noon": "2016-02-23T20:22:33+00:00",
                  "day_length": 38674,
                  "civil_twilight_begin": "2016-02-23T14:29:08+00:00",
                  "civil_twilight_end": "2016-02-24T02:15:58+00:00",
                  "nautical_twilight_begin": "2016-02-23T13:53:21+00:00",
                  "nautical_twilight_end": "2016-02-24T02:51:44+00:00",
                  "astronomical_twilight_begin": "2016-02-23T13:17:39+00:00",
                  "astronomical_twilight_end": "2016-02-24T03:27:26+00:00"
                }

        Raises:
            urllib.HTTPError: any errors from calling the API
        """

        args = {
            "date": astronomical_date,
            "lat": latitude,
            "lng": longitude,
            "formatted": 0,
        }
        url = self.API_BASE_URL % urlencode(args)
        self.logger.info(f"Calling API with {url}")

        with urlopen(url) as resource:
            response = json.load(resource)
            if "results" not in response or response["status"] != "OK":
                self.logger.info(f"API Raw Response {response}")
                raise APIError(
                    "Sunrise-Sunset API", "Malformed response, missing results")
            self.logger.debug(f"API Raw Response {response}")
            return response.get("results")

    def __format_data(self, data: dict) -> dict:
        """Convert API data into a timezone-appropriate format

        Args:
            data: see :function: __call_api

        Returns:
            A dictionary of formatted data::

                {...}

        """

        # the api results look like 2015-12-10T15:47:11+00:00
        utc_sr = parser.parse(data["sunrise"])
        # utc_sr.timestamp() -> int seconds since epoch
        sunrise_local_time = utc_sr.astimezone(tz.gettz(config.app["timezone"]))

        utc_ss = parser.parse(data["sunset"])
        sunset_local_time = utc_ss.astimezone(tz.gettz(config.app["timezone"]))

        return {
            # TODO what values are actually necessary for display?
            # day is stored in seconds and exact precision is not necessary
            "day_length": round(data["day_length"] / 60 / 60, 2),

            "date_utc": utc_sr.strftime("%Y-%m-%d"),
            "sunrise_utc": utc_sr.strftime("%H:%M:%S%z"),
            "sunset_utc": utc_ss.strftime("%H:%M:%S%z"),

            "date_local": sunrise_local_time.strftime("%Y-%m-%d"),
            "sunrise_local_time": sunrise_local_time.strftime("%H:%M:%S%z"),
            "sunset_local_time": sunset_local_time.strftime("%H:%M:%S%z")
        }

    def __set_local_data(self, data: dict) -> None:
        """Save astronomical data in the database.

        Args:
            data: see :function:: __call_api

        Returns:
            None

        """

        # TODO actually save data to database
        pass
