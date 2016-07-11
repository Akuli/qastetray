# Copyright (c) 2016 Akuli

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""Simple program for using online pastebins.

This program displays a paste icon in the system tray. The tray icon can
be clicked and new pastes to online pastebins can be easily made.
"""


# Add your name here if you've helped with making this program but your
# name is not here yet.
AUTHORS = ["Akuli"]
MAINTAINER = "Akuli"
TRANSLATORS = {
    'fi': "Akuli",
}

# General information.
SHORT_DESC, LONG_DESC = __doc__.split('\n\n', 1)
LONG_DESC = LONG_DESC.strip().replace('\n', ' ')

URL = 'https://github.com/Akuli/qastetray/'
VERSION = '1.0-dev'
KEYWORDS = ['pastebin', 'PyQt5']
USER_AGENT = 'QasteTray/' + VERSION

PIP_DEPENDS = ['requests', 'PyQt5']
DEBIAN_DEPENDS = ['python3-requests', 'python3-pyqt5']
