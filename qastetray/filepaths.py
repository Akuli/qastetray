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

"""The filepaths."""

import configparser
import os
import platform

try:
    # Some versions of PIP come with appdirs.
    from pip.utils import appdirs   # NOQA
except ImportError:
    # Otherwise appdirs needs to be installed.
    import appdirs      # NOQA


# Platform information.
platform = platform.system()


# Where is QasteTray installed?
def _get_dir(name):
    result = _dirconfig['InstallDirs'][name]
    result = result.split('/')
    result = os.path.join(pydir, *result)
    return os.path.abspath(result)

pydir = os.path.dirname(os.path.abspath(__file__))
_dirconfig = configparser.ConfigParser()
_dirconfig.read(os.path.join(pydir, 'dirs.conf'))
_dirconfig['InstallDirs']['sep'] = os.path.sep
docdir = _get_dir('docdir')
icondir = _get_dir('icondir')
localedir = _get_dir('localedir')


# User-wide configuration files.
app = 'QasteTray' if platform == 'Windows' else 'qastetray'
user_cache_dir = appdirs.user_cache_dir(app)
user_config_dir = appdirs.user_config_dir(app)
os.makedirs(user_cache_dir, exist_ok=True)
os.makedirs(user_config_dir, exist_ok=True)
