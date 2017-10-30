# -*- coding: utf-8 -*-

import datetime


class AtomDate:

    def __init__(self, timestamp):
        """
        In QuickTime File Format, date time is represented by seconds
        since midnight, Jan. 1, 1904.
        """

        self.date = datetime.datetime(1904, 1, 1, 0, 0,
                                      tzinfo=datetime.timezone.utc)
        self.date += datetime.timedelta(seconds=timestamp)

    def __str__(self):
        return self.date.strftime('%Y-%m-%dT%H:%M:%S%z')


class AtomMatrix:

    def __init__(self, matrix_data):
        """
        In QuickTime File Format, Matrix structure is stored in the
        order of a, b, u, c, d, v, x, y, w, where

           [a b u]
           [c d v]
           [x y w]

        with the all elements are 32-bit fixed-point numbers.
        u, v and w are divided as 2.30 and the others are divided as 16.16.
        """

        (self.a, self.b, self.u, self.c, self.d,
         self.v, self.x, self.y, self.w) = matrix_data

        self.a /= 2 ** 16
        self.b /= 2 ** 16
        self.c /= 2 ** 16
        self.d /= 2 ** 16
        self.x /= 2 ** 16
        self.y /= 2 ** 16

        self.u /= 2 ** 30
        self.v /= 2 ** 30
        self.w /= 2 ** 30

    def matrix(self):
        return (self.a, self.b, self.u, self.c, self.d,
                self.v, self.x, self.y, self.w)

    def __str__(self):
        return ("[[%16.16f %16.16f %2.30f] "
                "[%16.16f %16.16f %2.30f] "
                "[%16.16f %16.16f %2.30f]]" % self.matrix())
