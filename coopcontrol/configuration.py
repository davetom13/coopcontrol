# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
.. module:: configuration
    :synopsis: Read package configuration data for modules to use.

.. moduleauthor:: Toni Wells <isometimescode@users.noreply.github.com>

"""

from os import getenv, path
from pprint import pformat
import logging.config

import re
import yaml


class _Config:
    ENV = ""
    """Uses the COOPCONTROL_ENV environment variable"""

    def __init__(self):
        fname = path.join(
            path.dirname(path.dirname(__file__)), "data", "config.yaml")
        with open(fname) as file:
            self.config = yaml.safe_load(file)

        environment = getenv("COOPCONTROL_ENV")
        if environment not in self.config:
            raise ValueError(f"ENV {environment} not found or incorrect")

        # set ourselves to "development" or "production"
        self.ENV = environment

        # set up our logging configuration as specifed
        if "logging" in self.config[self.ENV]:
            logging.config.dictConfig(self.config[self.ENV]["logging"])

    def __str__(self):
        return pformat(self.config[self.ENV])

    def __getattr__(self, name):
        """Note: if you want a deep lookup, use the `get` method"""
        return self._replace_secrets(self.config[self.ENV][name])

    def get(self, name):
        """Find a value in the nested config

        Args:
            name: string name to search for, using dot notation

        Raises:
            AttributeError: when name can't be found

        Example::

          config.get("logging.formatters.simple") #=> {"key":"value"}
          config.get("app.name")                  #=> "string"
          config.get("foo")                       #=> AttributeError

        """

        def search(obj, key):
            if key in obj:
                return self._replace_secrets(obj[key])

            keys = key.split(".")
            if keys[0] not in obj:
                raise AttributeError(f"{keys[0]} was not found")

            return search(obj[keys[0]], ".".join(keys[1:]))

        return search(self.config[self.ENV], name)

    def _replace_secrets(self, value):
        if type(value) != str:
            return value

        # looking for secrets defined as {{SOME_ENV_VAR}}
        match = re.match(r"^{{([A-Z0-9_]+)}}$", value)
        if match and match.group(1) and getenv(match.group(1)):
            return getenv(match.group(1))

        # default, return whatever is in the config
        return value


config = _Config()
"""Main configuration instance.

Example::

    from coopcontrol.configuration import config
    print(config.get("app.name")

"""
