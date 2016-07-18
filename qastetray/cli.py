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

"""Run the CLI."""

import argparse
from gettext import gettext as _
import sys

from qastetray import VERSION
from qastetray.core import pastebin_manager, load_gettext


def error(msg, error_type=None):
    """Exit with an error message."""
    if error_type is None:
        error_type = _("error")
    sys.exit("qastetray-cli: {}: {}".format(error_type, msg))


class PastebinsAction(argparse.Action):
    """An argparse action for printing a list of available pastebins."""

    def __init__(self, *args, pastebin_names, nargs=0, help=None, **kwargs):
        """Initialize the action.

        full_name_dict should be a dictionary with abbreviated pastebin
        names as keys and non-abbreviated pastebin names as values.
        """
        if help is None:
            help = _("show a list of available pastebins and exit")
        super().__init__(*args, nargs=nargs, help=help, **kwargs)
        self.__pastebin_names = pastebin_names

    def __call__(self, parser, namespace, values, option_string=None):
        """Print the list of pastebins."""
        print(_("Supported pastebins:"))
        print()
        print(_("Full name").upper().ljust(20),
              _("Abbreviated name").upper())
        for abbreviated_name, full_name in self.__pastebin_names.items():
            print(full_name.ljust(20), abbreviated_name)
        parser.exit()


def main(args=None):
    """Run the CLI."""
    if args is None:
        args = sys.argv

    load_gettext()

    # Get a dictionary of abbreviated pastebin names.
    pastebin_manager.load()
    full_name_dict = {}
    for full_name in pastebin_manager.pastebins.keys():
        abbreviated_name = full_name.lower().replace(' ', '-')
        full_name_dict[abbreviated_name] = full_name

    parser = argparse.ArgumentParser(
        prog='qastetray-cli',
        description=_("Command-line interface for {}.").format("QasteTray"),
        add_help=False,
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-h', '--help', action='help',
        help=_("show this help message and exit"))
    group.add_argument(
        '-v', '--version', action='version',
        version='QasteTray {}'.format(VERSION),
        help=_("show {}'s version and exit").format("QasteTray"))
    group.add_argument(
        '-p', '--pastebins', action=PastebinsAction,
        pastebin_names=full_name_dict)

    parser.add_argument(
        'pastebin',
        help=_("an abbreviated pastebin name, see {}").format("--pastebins"))
    parser.add_argument(
        'file', nargs=argparse.OPTIONAL,
        help=_("input file, defaults to standard input"))
    parser.add_argument(
        '-e', '--expiry',
        help=_("expiry in days, defaults to smallest possible"))
    parser.add_argument(
        '-s', '--syntax',
        help=_("syntax highlighting, defaults to plain text"))
    parser.add_argument(
        '-t', '--title',
        help=_("the title of the paste"))
    parser.add_argument('-u', '--username', help=_("your username or nick"))

    args = parser.parse_args(args[1:])

    try:
        pastebin_name = full_name_dict[args.pastebin]
    except KeyError:
        error(_("unknown pastebin {!r}").format(args.pastebin))
    pastebin = pastebin_manager.pastebins[pastebin_name]

    if args.expiry is None:
        expiry = pastebin.expiry_days[0]
    else:
        try:
            expiry = int(args.expiry)
            if expiry not in pastebin.expiry_days:
                raise ValueError
        except ValueError:
            expirylist = ','.join(str(e) for e in pastebin.expiry_days)
            error(_("invalid expiry {expiry!r}, should be one of {should_be}")
                  .format(expiry=str(args.expiry), should_be=expirylist))

    try:
        if args.file is None:
            content = sys.stdin.read()
        else:
            with open(args.file, 'r') as f:
                content = f.read()
    except UnicodeError:
        error(_("non-Unicode input"))

    # This CLI shows complete error messages unlike the GUI's.
    url = pastebin_manager.paste(
        pastebin=pastebin,
        content=content,
        expiry=expiry,
        syntax=args.syntax,
        title=args.title,
        username=args.username,
    )
    print(url)

    sys.exit()


if __name__ == '__main__':
    main()
