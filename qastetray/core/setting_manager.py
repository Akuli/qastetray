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

"""Setting manager for QasteTray."""

import configparser
import os

from qastetray.core import filepaths


_configs = {}


def get(filename):
    """Load a configuration file.

    Return a configparser.ConfigParser. The parsers are cached, so if
    this function is called multiple times with the same argument it
    will always return the same parser.
    """
    if filename not in _configs:
        _configs[filename] = configparser.ConfigParser(
            dict_type=dict,         # No need for ordering
            interpolation=None,     # Allow % signs in values.
        )
        _configs[filename].read([
            os.path.join(filepaths.topdir, filename),
            os.path.join(filepaths.userconfigdir, filename),
        ])
    return _configs[filename]


def save():
    """Save all loaded configuration files."""
    for filename, config in _configs.items():
        path = os.path.join(filepaths.userconfigdir, filename)
        with open(path, 'w') as f:
            config.write(f)
