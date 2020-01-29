#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (c) 2015-2020 Toni Wells

"""
This script pulls astronomical (sunrise, sunset, etc) information and
saves it to the database. By default it will get the data for today.

Check available options:
    python astronomical_data.py -h

Crontab: runs every day at midnight
0 0 * * * python /full/path/astronomical_data.py
"""

import argparse
import sys

from coopcontrol.astronomical import Astronomical

sysparse = argparse.ArgumentParser(description="Retrieve and store sunrise/sunset/daylight data")
sysparse.add_argument('-d', '--date', default="today",
                      help="An optional date to check, default is today.")
sysargs = sysparse.parse_args()

astro = Astronomical()
results = astro.get_api_data(sysargs.date, True)
if results.get("db_id"):
    print(f"Results added for {sysargs.date}")
else:
    sys.exit(
        f"An error occurred saving the astronomical data; results: {results}")
