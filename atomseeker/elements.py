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


class AtomLanguageCodeValue:

    # Macintosh Language Codes
    MAC_LANGUAGE_CODE = (
        "English",
        "French",
        "German",
        "Italian",
        "Dutch",
        "Swedish",
        "Spanish",
        "Danish",
        "Portuguese",
        "Norwegian",
        "Hebrew",
        "Japanese",
        "Arabic",
        "Finnish",
        "Greek",
        "Icelandic",
        "Maltese",
        "Turkish",
        "Croatian",
        "Traditional",
        "Chinese",
        "Urdu",
        "Hindi",
        "Thai",
        "Korean",
        "Lithuanian",
        "Polish",
        "Hungarian",
        "Estonian",
        "Lettish",
        "Latvian",
        "Saami",
        "Sami",
        "Faroese",
        "Farsi",
        "Russian",
        "Simplified",
        "Chinese",
        "Flemish",
        "Irish",
        "Albanian",
        "Romanian",
        "Czech",
        "Slovak",
        "Slovenian",
        "Yiddish",
        "Serbian",
        "Macedonian",
        "Bulgarian",
        "Ukrainian",
        "Belarusian",
        "Uzbek",
        "Kazakh",
        "Azerbaijani",
        "AzerbaijanAr",
        "Armenian",
        "Georgian",
        "Moldavian",
        "Kirghiz",
        "Tajiki",
        "Turkmen",
        "Mongolian",
        "MongolianCyr",
        "Pashto",
        "Kurdish",
        "Kashmiri",
        "Sindhi",
        "Tibetan",
        "Nepali",
        "Sanskrit",
        "Marathi",
        "Bengali",
        "Assamese",
        "Gujarati",
        "Punjabi",
        "Oriya",
        "Malayalam",
        "Kannada",
        "Tamil",
        "Telugu",
        "Sinhala",
        "Burmese",
        "Khmer",
        "Lao",
        "Vietnamese",
        "Indonesian",
        "Tagalog",
        "MalayRoman",
        "MalayArabic",
        "Amharic",
        "Galla",
        "Oromo",
        "Somali",
        "Swahili",
        "Kinyarwanda",
        "Rundi",
        "Nyanja",
        "Malagasy",
        "Esperanto",
        "Welsh",
        "Basque",
        "Catalan",
        "Latin",
        "Quechua",
        "Guarani",
        "Aymara",
        "Tatar",
        "Uighur",
        "Dzongkha",
        "JavaneseRom",

    )

    def __init__(self, value):

        # the value should be less than 0x8000
        if value > 0x7fff:
            raise ValueError

        self.value = value

    def __str__(self):

        if self.value < 0x400:
            return MAC_LANGUAGE_CODE[self.value]
        elif self.value == 0x7fff:
            return 'Unspecified'
        else:
            return "%c%c%c" % (((self.value >> 10) & 0x1f) + 0x60,
                               ((self.value >> 5) & 0x1f) + 0x60,
                               (self.value & 0x1f) + 0x60)
