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

"""Setting manager for QasteTray.

The setting changing dialog is in setting_dialog.py.
"""

import configparser
import os

from qastetray import filepaths


_DEFAULT_SETTINGS = os.path.join(filepaths.pydir, 'qastetray.conf')
_USER_SETTINGS = os.path.join(filepaths.user_config_dir, 'qastetray.conf')

settings = configparser.ConfigParser(
    dict_type=dict,         # No need for ordering.
    interpolation=None,     # Allow % in values.
)


def load():
    """Load configuration files."""
    settings.read([_DEFAULT_SETTINGS, _USER_SETTINGS])


def save():
    """Save to the user-wide configuration files."""
    with open(_USER_SETTINGS, 'w') as f:
        print("# Configuartion file for QasteTray.", file=f)
        settings.write(f)
