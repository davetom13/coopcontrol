# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
.. module:: exception
    :synopsis: Provide custom exceptions for this package.

.. moduleauthor:: Toni Wells <isometimescode@users.noreply.github.com>

"""

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class APIError(Error):
    """Exception raised for errors during external API requests.

    Attributes:
        api_name: api for which the error occurred
        message: explanation of the error
    """

    def __str__(self):
        return "Error calling {self.api_name}: {self.message}"

    def __init__(self, api_name, message):
        self.api_name = api_name
        self.message = message
