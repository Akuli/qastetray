"""New paste window."""

from gettext import gettext as _
import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                             QProgressBar, QPushButton, QSizePolicy, QTextEdit,
                             QVBoxLayout, QWidget)

from qastetray import backend, settings


# The paste windows are added here to avoid garbage collection.
_new_paste_windows = []


class _ContentTextEdit(QTextEdit):

    def __init__(self):
        super().__init__()
        self._style_sheet = {}
        settings.add_postfunc('NewPasteWindow', 'font', self._set_font)
        settings.add_postfunc('NewPasteWindow', 'fgcolor', self._set_fg)
        settings.add_postfunc('NewPasteWindow', 'bgcolor', self._set_bg)

    def _set_font(self, font_string):
        font = QFont()
        font.fromString(font_string)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

    def _set_fg(self, color_name):
        self._style_sheet['color'] = color_name
        self._apply_style_sheet()

    def _set_bg(self, color_name):
        self._style_sheet['background-color'] = color_name
        self._apply_style_sheet()

    def _apply_style_sheet(self):
        props = (': '.join(prop) for prop in self._style_sheet.items())
        self.setStyleSheet('; '.join(props))

    def remove_postfuncs(self):
        """Remove postfuncs added in __init__.

        Run this method before destroying the window this widget is in.
        """
        settings.remove_postfunc('NewPasteWindow', 'font', self._set_font)
        settings.remove_postfunc('NewPasteWindow', 'fgcolor', self._set_fg)
        settings.remove_postfunc('NewPasteWindow', 'bgcolor', self._set_bg)


class PasteSuccessDialog(QDialog):
    """A dialog for showing the paste URL to the user."""

    def __init__(self, url, parent=None):
        """Initialize the dialog and create widgets."""
        super().__init__(parent)
        self._url = url

        layout = QVBoxLayout()
        self.setLayout(layout)

        label = QLabel(_("Pasting succeeded."))
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        layout.addWidget(label)

        line_edit = QLineEdit()
        line_edit.setText(url)
        line_edit.selectAll()
        line_edit.setToolTip(_("Highlight and press Ctrl+C to copy"))
        line_edit.setReadOnly(True)
        layout.addWidget(line_edit)

        layout.addStretch(1)

        buttonbox = QDialogButtonBox()
        layout.addWidget(buttonbox)

        browser_button = QPushButton(_("O&pen in browser"))
        browser_button.clicked.connect(self._open_in_browser_clicked)
        buttonbox.addButton(browser_button, QDialogButtonBox.ApplyRole)

        ok_button = QPushButton("&OK")
        ok_button.clicked.connect(self.close)
        buttonbox.addButton(ok_button, QDialogButtonBox.AcceptRole)

    def _open_in_browser_clicked(self):
        webbrowser.open(self._url)
        self.close()


class _NewPasteWindow(QWidget):

    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout()
        self.setLayout(vbox)

        self._create_edits()
        self._create_forms()
        self._create_bottom_widgets()

    def _create_edits(self):
        """Create the title line edit and content text edit."""
        self._title_line_edit = QLineEdit()
        self._title_line_edit.setToolTip(_("Title of your paste (optional)"))
        self.layout().addWidget(self._title_line_edit)

        # TODO: Use a monospace font.
        self._content_text_edit = _ContentTextEdit()
        self._content_text_edit.setToolTip(_("The content to paste"))
        self.layout().addWidget(self._content_text_edit)

    def _create_forms(self):
        """Create the 'forms' in the middle."""
        self._pastebin_combo = pastebin = QComboBox()
        self._expiry_combo = expiry = QComboBox()
        self._name_line_edit = name = QLineEdit()
        self._syntax_line_edit = syntax = QLineEdit()

        # This is not a form layout because it has four columns instead
        # of two.
        grid = QGridLayout()
        self.layout().addLayout(grid)

        widgets = [
            (_("Pastebin:"), pastebin, _("Name or nick:"), name),
            (_("Expiry:"), expiry, _("Syntax highlighting:"), syntax),
        ]
        for y, row in enumerate(widgets):
            for x, item in enumerate(row):
                if isinstance(item, str):
                    item = QLabel(item)
                else:
                    # The item must expand more than the label.
                    policy = item.sizePolicy()
                    policy.setHorizontalPolicy(QSizePolicy.Expanding)
                    item.setSizePolicy(policy)
                grid.addWidget(item, y, x)

    def _create_bottom_widgets(self):
        """Create the progressbar and buttons."""
        hbox = QHBoxLayout()
        self.layout().addLayout(hbox)

        progressbar = self._progressbar = QProgressBar()
        hbox.addWidget(progressbar)

        ok_button = QPushButton(_("Paste!"))
        ok_button.clicked.connect(self._paste)
        hbox.addWidget(ok_button)

        cancel_button = QPushButton(_("Cancel"))
        cancel_button.clicked.connect(self.close)
        hbox.addWidget(cancel_button)

    def _paste(self):
        """Start pasting."""
        self._progressbar.setRange(0, 0)  # Moving back and forth.
        pastebin = backend.pastebins['dpaste']
        getters = {
            'content': self._content_text_edit.toPlainText,
            'expiry': lambda: 1,
            'syntax': lambda: 'text',
            'title': self._title_line_edit.text,
            'username': self._name_line_edit.text,
        }
        self._pasting_thread = backend.PastingThread(pastebin, getters)
        self._pasting_thread.finished.connect(self._pasting_finished)
        self._pasting_thread.start()

    def _pasting_finished(self):
        """End pasting."""
        self._progressbar.setRange(0, 1)  # Staying at 0%.
        if self._pasting_thread.success:
            dialog = PasteSuccessDialog(self._pasting_thread.response, self)
            dialog.resize(300, 200)
            dialog.exec_()
            self.close()
        else:
            QMessageBox.critical(
                self, _("Error"), '\n'.join([
                    _("Pasting failed!"),
                    self._pasting_thread.response,
                    _("Make sure you have an internet connection or try"
                      "another pastebin."),
                ]), QMessageBox.Ok, QMessageBox.Ok,
            )

    def closeEvent(self, event):
        """Close and delete the window if user wants to."""
        content = self._content_text_edit.toPlainText()
        ask = settings.get_bool('NewPasteWindow', 'ask-on-quit')
        try:
            success = self._pasting_thread.success
        except AttributeError:
            success = False

        if content and ask and not success:
            # The user may want to save something.
            reply = QMessageBox.question(
                self, _("Quit without pasting"),
                _("Quit without making a paste?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes,
            )
            if reply == QMessageBox.No:
                event.ignore()
                return
        self._content_text_edit.remove_postfuncs()
        _new_paste_windows.remove(self)
        event.accept()


def new_paste():
    """Create a new paste."""
    window = _NewPasteWindow()
    window.setWindowTitle("New paste")
    window.resize(600, 400)
    window.show()
    _new_paste_windows.append(window)
