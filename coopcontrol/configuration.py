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
        return self.config[self.ENV][name]

config = _Config()
"""Main configuration instance.

Example::

    from coopcontrol.configuration import config
    print(config.app["name"])

"""
