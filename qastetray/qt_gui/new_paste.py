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

"""New paste window."""

from gettext import gettext as _
import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets

from qastetray.core import pastebin_manager
from qastetray.core.setting_manager import settings


# The paste windows are added here to avoid garbage collection.
_new_paste_windows = []


class _SyntaxHBox(QtWidgets.QHBoxLayout):
    """A HBox layout for the syntax line edit."""

    def __init__(self, parent=None):
        """Initialize the HBox and add widgets to it."""
        super().__init__(parent)

        self._line_edit = QtWidgets.QLineEdit()
        self._line_edit.textChanged.connect(self._on_text_changed)
        self.addWidget(self.line_edit)

        icon = QtWidgets.QIcon.fromTheme('dialog-warning')
        size = self._line_edit.sizeHint().height()
        size = icon.actualSize(QtWidgets.QSize(size, size))
        self._icon = QtWidgets.QLabel()
        self._icon.setToolTip(_("Invalid syntax choice"))
        self._icon.setPixmap(icon.pixmap(size))
        self.addWidget(self._icon)

    def _on_text_changed(self, text):
        """Show or hide the icon."""
        if self._syntaxes and text in self._syntaxes:
            self._icon.hide()
        else:
            self._icon.show()

    def set_pastebin(self, pastebin):
        """Call this when the pastebin is changed."""
        # Check if this widget is needed.
        if 'syntax' not in pastebin.paste_args:
            # This widget is not needed.
            self.setEnabled(False)
            return
        self.setEnabled(True)

        # Autocompletions.
        self._syntaxes = sorted(
            getattr(pastebin, 'syntax_choices', {}).keys(),
            key=str.lower)
        completer = QtWidgets.QCompleter(self._syntaxes)
        completer.setFilterMode(QtWidgets.Qt.MatchContains)
        completer.setCaseSensitivity(QtWidgets.Qt.CaseInsensitive)
        self._line_edit.setCompleter(completer)

        # Current selection.
        syntax = settings['DefaultSyntax'].get(pastebin.name)
        if syntax not in self._syntaxes:
            syntax = pastebin.syntax_default
        self._line_edit.setText(syntax)


class _PasteSuccessDialog(QtWidgets.QDialog):
    """A dialog for showing the paste URL to the user."""

    def __init__(self, url, *args, **kwargs):
        """Initialize the dialog and create widgets."""
        super().__init__(*args, **kwargs)
        self._url = url

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        label = QtWidgets.QLabel(_("Pasting succeeded."))
        label.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        main_layout.addWidget(label)

        line_edit = QtWidgets.QLineEdit()
        line_edit.setText(url)
        line_edit.selectAll()
        line_edit.setToolTip(_("Highlight and press Ctrl+C to copy"))
        line_edit.setReadOnly(True)
        main_layout.addWidget(line_edit)

        main_layout.addStretch(1)

        buttonbox = QtWidgets.QDialogButtonBox()
        main_layout.addWidget(buttonbox)

        browser_button = QtWidgets.QPushButton(_("O&pen in browser"))
        browser_button.clicked.connect(self._open_in_browser_clicked)
        buttonbox.addButton(browser_button,
                            QtWidgets.QDialogButtonBox.ApplyRole)

        ok_button = QtWidgets.QPushButton("&OK")
        ok_button.clicked.connect(self.close)
        buttonbox.addButton(ok_button, QtWidgets.QDialogButtonBox.AcceptRole)

    def _open_in_browser_clicked(self):
        webbrowser.open(self._url)
        self.close()

    def run(self):
        """Paste."""


class PastingThread(QtCore.QThread):
    """A thread for pasting."""

    def __init__(self, pastebin, getters):
        """Initialize the thread.

        The getters argument should be a dictionary of possible pastebin
        paste_args and functions or methods for getting values for them.
        This way the getters for arguments not supported by the pastebin
        are not called.
        """
        super().__init__()
        self._pastebin = pastebin
        self._kwargs = {arg: getters[arg]() for arg in pastebin.paste_args}


class _NewPasteWindow(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        # Title line edit.
        self._title_line_edit = QtWidgets.QLineEdit()
        self._title_line_edit.setToolTip(_("Title of your paste (optional)"))
        main_layout.addWidget(self._title_line_edit)

        # Content text edit.
        content = self._content_text_edit = QtWidgets.QTextEdit()
        content.setToolTip(_("The content to paste"))
        content.setStyleSheet('color: {fg}; background-color: {bg}'.format(
            fg=settings['NewPasteWindow']['fgcolor'],
            bg=settings['NewPasteWindow']['bgcolor'],
        ))
        main_layout.addWidget(content)

        font = QtGui.QFont()
        font.fromString(settings['NewPasteWindow']['font'])
        font.setStyleHint(QtGui.QFont.Monospace)
        content.setFont(font)

        # 'Forms' in the middle.
        self._pastebin_combo = QtWidgets.QComboBox()
        self._pastebin_combo.addItems(
            sorted(pastebin_manager.pastebins.keys(), key=str.lower))
        self._pastebin_combo.currentTextChanged.connect(
            self._on_pastebin_changed)

        self._expiry_combo = QtWidgets.QComboBox()

        self._name_line_edit = QtWidgets.QLineEdit()

        # The syntax combobox has an icon next to it.
        self._syntax_hbox = QtWidgets.QHBoxLayout()

        self._syntax_line_edit = QtWidgets.QLineEdit()
        self._syntax_completer = QtWidgets.QCompleter()
        self._syntax_hbox.addWidget(self._syntax_line_edit)

        icon = QtWidgets.QIcon.fromTheme('dialog-warning')
        size = self._syntax_line_edit.sizeHint().height()
        pixmap = icon.pixmap(icon.actualSize(QtWidgets.QSize(size, size)))
        self._syntax_icon = QtWidgets.QLabel()
        self._syntax_icon.setPixmap(pixmap)
        self._syntax_icon.hide()
        self._syntax_hbox.addWidget(self._syntax_icon)

        # This is not a form layout because it has four columns instead
        # of two.
        grid = QtWidgets.QGridLayout()
        main_layout.addLayout(grid)

        # These widgets must expand more than the labels.
        for widget in (self._pastebin_combo, self._name_line_edit,
                       self._expiry_combo, self._syntax_hbox.line_edit):
            policy = widget.sizePolicy()
            policy.setHorizontalPolicy(QtWidgets.QSizePolicy.Expanding)
            widget.setSizePolicy(policy)

        grid.addWidget(QtWidgets.QLabel(_("Pastebin:")), 0, 0)
        grid.addWidget(self._pastebin_combo, 0, 1)
        grid.addWidget(QtWidgets.QLabel(_("Name or nick:")), 1, 0)
        grid.addWidget(self._name_line_edit, 1, 1)
        grid.addWidget(QtWidgets.QLabel(_("Expiry:")), 0, 2)
        grid.addWidget(self._expiry_combo, 0, 3)
        grid.addWidget(QtWidgets.QLabel(_("Syntax highlighting:")), 1, 2)
        grid.addLayout(self._syntax_hbox, 1, 3)

        # Progress bar and buttons.
        hbox = QtWidgets.QHBoxLayout()
        main_layout.addLayout(hbox)

        progressbar = self._progressbar = QtWidgets.QProgressBar()
        hbox.addWidget(progressbar)

        self._paste_button = QtWidgets.QPushButton(_("Paste!"))
        self._paste_button.clicked.connect(self._paste)
        hbox.addWidget(self._paste_button)

        self._cancel_button = QtWidgets.QPushButton(_("Cancel"))
        self._cancel_button.clicked.connect(self.close)
        hbox.addWidget(self._cancel_button)

    def _on_pastebin_changed(self, new_name):
        pastebin = pastebin_manager.pastebins[new_name]
        print(pastebin)

        # Syntax highlighting.
        if 'syntax' in pastebin.paste_args:
            self._syntax_hbox.setEnabled(True)
            completions = pastebin.syntax_choices.keys()
            self._syntax_completer.model().setStringList(completions)
            syntax = settings['DefaultSyntax'][new_name]
        else:
            self._syntax_hbox.setEnabled(False)

        # Expiry.
        if 'expiry' in pastebin.paste_args:
            self._expiry_combo.setEnabled(True)
            self._expiry_combo.clear()
            for expiry in pastebin.expiry_days:
                if expiry < 0:
                    text = _("Never delete this paste")
                else:
                    text = _("Delete this paste in {} days").format(expiry)
                self._expiry_combo.addItem(text)
#            self._expiry_combo.
        else:
            self._expiry_combo.setEnabled(False)

    def _paste(self):
        """Start pasting."""
        self._progressbar.setRange(0, 0)  # Move back and forth.
        self.setEnabled(False)
        pastebin = pastebin_manager.pastebins['dpaste']
        getters = {
            'content': self._content_text_edit.toPlainText,
            'expiry': lambda: 1,
            'syntax': lambda: 'text',
            'title': self._title_line_edit.text,
            'username': self._name_line_edit.text,
        }
        self._pasting_thread = PastingThread(pastebin, getters)
        self._pasting_thread.finished.connect(self._pasting_finished)
        self._pasting_thread.start()

    def _paste_with_pastebin(self):
        """Lol."""

    def _pasting_finished(self):
        """End pasting."""
        self._progressbar.setRange(0, 1)  # Stay at 0%.
        self.setEnabled(True)
        if self._pasting_thread.success:
            dialog = _PasteSuccessDialog(self._pasting_thread.response, self)
            dialog.resize(300, 200)
            dialog.exec_()
            self.close()
        else:
            msg = '\n'.join([
                _("Pasting failed!"),
                self._pasting_thread.response,
                _("Make sure you have an internet connection or try"
                  "another pastebin."),
            ])
            QtWidgets.QMessageBox.critical(
                self, _("Error"), msg, QtWidgets.QMessageBox.Ok,
                QtWidgets.QMessageBox.Ok,
            )

    def closeEvent(self, event):
        """Close and delete the window if user wants to."""
        try:
            not_pasted_yet = not self._pasting_thread.success
        except AttributeError:
            not_pasted_yet = True

        if (
          settings.getboolean('NewPasteWindow', 'ask-on-quit') and
          self._content_text_edit.toPlainText() and
          not_pasted_yet):
            # The user may want to save something.
            reply = QtWidgets.QMessageBox.question(
                self, _("QtWidgets.Quit without pasting"),
                _("QtWidgets.Quit without making a paste?"),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.Yes,
            )
            if reply == QtWidgets.QMessageBox.No:
                event.ignore()
                return
        _new_paste_windows.remove(self)
        event.accept()


def new_paste():
    """Create a new paste."""
    window = _NewPasteWindow()
    window.setWindowTitle("New paste")
    window.resize(600, 400)
    window.show()
    _new_paste_windows.append(window)
