# -*- coding: utf-8 -*-

import time

# Weekday and month names for HTTP date/time formatting; always English!
WEEKDAY_NAME = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTH_NAME = [None,  # Dummy so we can use 1-based month numbers
              "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def format_date_time(timestamp):
    year, month, day, hh, mm, ss, wd, y, z = time.gmtime(timestamp)
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (WEEKDAY_NAME[wd],
                                                    day,
                                                    MONTH_NAME[month],
                                                    year, hh, mm, ss)
