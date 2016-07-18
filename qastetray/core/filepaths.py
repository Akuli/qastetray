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
import site


# This is where QasteTray is installed, and default pastebins are here.
def _get_dir(name):
    """Get a directory."""
    result = _dirconfig['InstallDirs'][name]
    result = os.path.join(topdir, result)
    return os.path.abspath(result)

topdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_dirconfig = configparser.ConfigParser(
    dict_type=dict,
    interpolation=configparser.ExtendedInterpolation(),
)
_dirconfig.read([os.path.join(topdir, 'dirs.conf')])
_dirconfig['InstallDirs']['pardir'] = os.path.pardir
_dirconfig['InstallDirs']['sep'] = os.path.sep
docdir = _get_dir('doc')
icondir = _get_dir('icons')
localedir = _get_dir('locale')


# User-wide pastebins will be here.
usersitedir = site.getusersitepackages()
site.addsitedir(usersitedir)
usersitedir = os.path.join(usersitedir, 'qastetray')

# Settings will be in user_config and temporary files in user_cache.
if 'APPDATA' in os.environ and 'TEMP' in os.environ:
    # Windows.
    usercachedir = os.path.join(os.getenv('TEMP'), 'QasteTray')
    userconfigdir = os.path.join(os.getenv('APPDATA'), 'QasteTray')
elif platform.system() == 'Darwin':
    # Mac OSX.
    usercachedir = os.path.expanduser('~/Library/Caches/QasteTray')
    userconfigdir = os.path.expanduser(
        '~/Library/Application Support/QasteTray')
else:
    # Probably other UNIX-like. /tmp cannot be used because these must
    # be user-specific.
    usercachedir = os.path.expanduser('~/.cache/qastetray')
    userconfigdir = os.path.expanduser('~/.config/qastetray')

os.makedirs(usersitedir, exist_ok=True)
os.makedirs(usercachedir, exist_ok=True)
os.makedirs(userconfigdir, exist_ok=True)
