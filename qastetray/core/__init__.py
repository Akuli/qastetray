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

"""Define more functions."""

import gettext
import os
from urllib.request import pathname2url
import webbrowser

from qastetray.core import filepaths


def load_gettext():
    """Set up gettext."""
    gettext.bindtextdomain('qastetray', filepaths.localedir)
    gettext.textdomain('qastetray')


def help():
    """Display the help HTML page in a web browser."""
    path = os.path.join(filepaths.docdir, 'index.html')
    url = 'file://' + pathname2url(path)

    # On X.Org, webbrowser.open() uses xdg-open by default instead of
    # x-www-browser, so HTML files don't always open in a WWW browser.
    try:
        webbrowser.get('x-www-browser').open(url)
    except webbrowser.Error:
        webbrowser.open(url)
