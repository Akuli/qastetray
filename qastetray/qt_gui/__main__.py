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

"""Run QasteTray with a GUI."""

import argparse
from gettext import gettext as _
import sys
import time

from PyQt5 import QtWidgets

from qastetray.core import lock, load_gettext, pastebin_manager, recent_paste_manager, setting_manager
from qastetray.qt_gui import new_paste, setting_dialog


def main(args=None):
    """Run the program."""
    if args is None:
        args = sys.argv

    load_gettext()

    # The description is not taken from other files because gettext is
    # not set up when they are ran.
    # TODO: Add arguments to parse.
    parser = argparse.ArgumentParser(description=_("Simple pastebin client."))
    parser.parse_args(args[1:])

    try:
        with lock.locked():
            app = QtWidgets.QApplication(args)
            pastebin_manager.load()
            recent_paste_manager.load()
#            setting_dialog.run()
            new_paste.new_paste()
    except lock.IsLocked:
        QtWidgets.QMessageBox.info(
            "QasteTray", _("{} is already running.").format("QasteTray"),
            QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok,
        )
        sys.exit()
    finally:
        setting_manager.save()
        recent_paste_manager.save()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
