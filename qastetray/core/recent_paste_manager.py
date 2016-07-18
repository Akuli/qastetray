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

"""Manage recent pastes.

The recent paste list is stored as json in the settings.
"""

import json

from qastetray.core import setting_manager


_settings = setting_manager.get('core.conf')['RecentPastes']


class _RecentPastes:
    """An iterable data structure for managing recent pastes.

    This is much like collections.deque, but the maxlen can be changed.
    Recent pastes are added to the beginning of the list with .add(),
    and they will be removed from the end when the list is longer than
    the maxlen. This may happen when items are added or the maxlen is
    changed.

    The maxlen can be negative or 0 to allow an infinite number of
    recent pastes or no recent pastes at all.
    """

    def __init__(self):
        """Initialize an empty recent paste list with maxlen -1."""
        self.__list = []
        self.__maxlen = -1

    def clear(self):
        """Remove all recent pastes."""
        self.__list.clear()

    @property
    def maxlen(self):
        """Maximum number of recent pastes."""
        return self.__maxlen

    @maxlen.setter
    def maxlen(self, maxlen):
        self.__maxlen = int(maxlen)
        self._shorten_to_maxlen()

    def add(self, url, title=''):
        """Insert a recent paste to the beginning of the list.

        If title is falsy or omitted, it defaults to url.
        """
        self.__list.insert(0, (url, title or url))
        self._shorten_to_maxlen()

    def _shorten_to_maxlen(self):
        """Make the recent paste list shorter or as long as maxlen."""
        if self.maxlen >= 0:
            del self.__list[self.maxlen:]

    def __getitem__(self, item):
        """Implement self[int(item)]."""
        if isinstance(item, slice):
            raise TypeError("cannot slice {} objects"
                            .format(type(self).__name__))
        return self.__list[int(item)]

    def __len__(self):
        """Implement len(self)."""
        return len(self.__list)


recent_pastes = _RecentPastes()


def load():
    """Load recent pastes."""
    recent_pastes.clear()
    recent_pastes.maxlen = _settings.getint('maxlen')
    for args in json.loads(_settings['json']):
        recent_pastes.add(*args)


def save():
    """Save the list of recent pastes to settings."""
    # The json module doesn't handle sequences correctly if they don't
    # inherit from list or tuple.
    pastelist = list(recent_pastes)
    _settings['json'] = json.dumps(pastelist)
