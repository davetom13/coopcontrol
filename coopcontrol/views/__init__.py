# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""Common methods for views.

Author: Toni Wells <isometimescode@users.noreply.github.com>

"""

def format_response(data, status_code=None, error_message=None):
    if data:
        retval = {"result": data}
    else:
        retval = {"result": dict()}

    if error_message:
        if not status_code:
            raise ValueError("status_code must be set with error_message")

        retval["message"] = error_message
        retval["status"] = "ERROR"
        return (retval, status_code)

    if not data:
        if not status_code:
            status_code = 404
        retval["status"] = "NOT_FOUND"
        return (retval, status_code)

    retval["status"] = "OK"
    if not status_code:
        status_code = 200
    return (retval, status_code)
