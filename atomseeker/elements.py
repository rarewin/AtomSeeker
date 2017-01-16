# -*- coding: utf-8 -*-

import datetime

class AtomDate:

    def __init__(self, timestamp):
        """
        In QuickTime File Format, date time is represented by seconds since midnight, Jan. 1, 1904.
        """

        print(timestamp)

        self.date = datetime.datetime(1904, 1, 1, 0, 0, tzinfo = datetime.timezone.utc)
        self.date += datetime.timedelta(seconds = timestamp)

    def __str__(self):
        return self.date.strftime('%Y-%m-%dT%H:%M:%S%z')
