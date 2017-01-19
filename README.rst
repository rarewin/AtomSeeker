AtomSeeker
==========

Abstract
--------

This is for analyzing Apple's QuickTime format files.
You can find a specification of QuickTime File Format(QTFF) at <https://developer.apple.com/library/content/documentation/QuickTime/QTFF/QTFFPreface/qtffPreface.html>.

Installing
----------

Please try the usual way as the follwing:

    % python setup.py install

Usage
-----

First, my aim is to generate html page from movie files.
At the moment the following command will output a small amount of information of [input_file] as text.

    % atomseek [input_file]


TODO
----

* command line options
* html generator (I plan to use jinja2)
* a lot of atoms not yet implemented

License
-------

This program is under the BSD 2-Clause License.
Please see LISENCE.txt.
