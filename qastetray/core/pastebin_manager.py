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

"""Load and manage pastebins.

The actual pastebin files are in qastetray.pastebins. It's a namespace
package, so users can create and use their own pastebins without access
to QasteTray's installation location. This module is called
pastebin_manager to avoid confusing it with qastetray.pastebins.

Pasting with a pastebin is simple. Select a pastebin from the pastebins
dictionary, and call its paste method with arguments defined in its
paste_args.
"""

import importlib
import os
import re
import sys


pastebins = {}
loaders = {}


def load():
    """Load the pastebins."""
    pastebins.clear()
    for directory in sys.path:
        directory = os.path.join(directory, 'qastetray', 'pastebins')
        if not os.path.isdir(directory):
            continue

        for filename in os.listdir(directory):
            match = re.search(r'^[a-z][a-z0-9_]*(\.[a-z]+)$', filename)
            if match is None:
                # Not a valid QasteTray pastebin.
                continue

            extension = match.group(1)
            if extension not in loaders:
                # The pastebin format is not supported.
                continue

            loader = loaders[extension]
            filepath = os.path.join(directory, filename)
            pastebin = loader(filepath)
            pastebins[pastebin.name] = pastebin


def paste(pastebin, content, expiry, syntax, title, username):
    """Paste with a pastebin.

    Arguments:
      pastebin: a pastebin from the pastebins dictionary
      content:  the content to paste
      expiry:   expiry in days from pastebin.expiry_days
      syntax:   a syntax choice
      title:    title of the paste or a falsy value
      username: nick, username or a falsy value

    If syntax_choice is a key from pastebin.syntax_choices, a value will
    be used instead.

    Return the URL of the newly created paste.
    """
    kwargs = {'content': content}
    if 'expiry' in pastebin.paste_args:
        kwargs['expiry'] = expiry
    if 'syntax' in pastebin.paste_args:
        # TODO: use syntax_default
        kwargs['syntax'] = pastebin.syntax_choices.get(syntax, syntax)
    if 'title' in pastebin.paste_args:
        kwargs['title'] = title or ''
    if 'username' in pastebin.paste_args:
        kwargs['username'] = username

    return pastebin.paste(**kwargs)


# Rest of this file is loader definitions. More loaders can be added to
# support storing pastebin information in different file formats.

# The loaders can be classes or functions, and they will be called with
# the full path to the pastebin file as the only argument. The loaders
# should be added to the loaders dictionary with their file extensions
# as keys.


def _import_loader(filepath):
    """Load a pastebin with an import."""
    # The filepath has been found by iterating sys.path, so importing it
    # is easy.
    basename = os.path.basename(filepath)
    modulename, ext = os.path.splitext(basename)
    modulename = 'qastetray.pastebins.{}'.format(modulename)

    # Hack to allow reloading
    try:
        del sys.modules[modulename]
    except Exception:
        pass

    return importlib.import_module(modulename)

loaders['.py'] = _import_loader
loaders['.pyc'] = _import_loader
loaders['.so'] = _import_loader     # Pastebins can be written in C.
loaders['.pyd'] = _import_loader


# TODO: Add an XML, JSON or .conf loader and port some of the default
# pastebins to use it.
