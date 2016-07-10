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

Unlike a plain configparser.ConfigParser instance, this module provides
a postfunc system and setters for integers, floats and Booleans.

The setting changing dialog is in setting_dialog.py.
"""

from configparser import ConfigParser
import os

from qastetray import filepaths


_DEFAULT_CONFIG = os.path.join(filepaths.pydir, 'qastetray.conf')
_USER_CONFIG = os.path.join(filepaths.user_config_dir, 'qastetray.conf')

_postfuncs = {}  # {(section, key): set of functions and methods, ...}
parser = ConfigParser(
    dict_type=dict,         # No need for ordering.
    interpolation=None,     # Allow % in values.
)


def set_str(section, key, value):
    """Set a string."""
    parser[section][key] = str(value)
    try:
        postfuncs = _postfuncs[section, key]
    except KeyError:
        pass    # No postfuncs.
    else:
        for func in postfuncs:
            func()


def set_int(section, key, value):
    """Set an integer."""
    set_str(section, key, int(value))


def set_float(section, key, value):
    """Set a floating point number."""
    set_str(section, key, float(value))


def set_bool(section, key, value):
    """Set a Boolean."""
    set_str(section, key, 'yes' if value else 'no')


def get_str(section, key):
    """Get a string."""
    return parser[section][key]


def get_int(section, key):
    """Get an integer."""
    return int(get_str(section, key))


def get_float(section, key):
    """Get a floating point number."""
    return float(get_str(section, key))


def get_bool(section, key):
    """Get a Boolean."""
    return ConfigParser.BOOLEAN_STATES[get_str(section, key)]


def add_postfunc(section, key, func, *, run_now=True):
    """Add a function that will be run when a value is changed.

    The function will be called with the new string value as its only
    argument. If run_now is True, func will be run when this function is
    called with the current value.
    """
    try:
        _postfuncs[section, key].add(func)
    except KeyError:
        _postfuncs[section, key] = {func}
    if run_now:
        func(get_str(section, key))


def remove_postfunc(section, key, func):
    """Remove a function added with add_postfunc."""
    _postfuncs[section, key].remove(func)


def load():
    """Load configuration files."""
    parser.read([_DEFAULT_CONFIG, _USER_CONFIG])


def save():
    """Save to the user-wide configuration files."""
    with open(_USER_CONFIG, 'w') as f:
        print("# Configuartion file for QasteTray.", file=f)
        parser.write(f)
