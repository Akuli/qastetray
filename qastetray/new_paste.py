"""New paste window."""

from gettext import gettext as _
import webbrowser

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QComboBox, QDialog, QDialogButtonBox, QGridLayout,
                             QHBoxLayout, QLabel, QLineEdit, QMessageBox,
                             QProgressBar, QPushButton, QSizePolicy, QTextEdit,
                             QVBoxLayout, QWidget)

from qastetray import backend
from qastetray.settings import settings


# The paste windows are added here to avoid garbage collection.
_new_paste_windows = []


class PasteSuccessDialog(QDialog):
    """A dialog for showing the paste URL to the user."""

    def __init__(self, url, parent=None):
        """Initialize the dialog and create widgets."""
        super().__init__(parent)
        self._url = url

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        label = QLabel(_("Pasting succeeded."))
        label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        main_layout.addWidget(label)

        line_edit = QLineEdit()
        line_edit.setText(url)
        line_edit.selectAll()
        line_edit.setToolTip(_("Highlight and press Ctrl+C to copy"))
        line_edit.setReadOnly(True)
        main_layout.addWidget(line_edit)

        main_layout.addStretch(1)

        buttonbox = QDialogButtonBox()
        main_layout.addWidget(buttonbox)

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

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Title line edit.
        self._title_line_edit = QLineEdit()
        self._title_line_edit.setToolTip(_("Title of your paste (optional)"))
        main_layout.addWidget(self._title_line_edit)

        # Content text edit.
        content = self._content_text_edit = QTextEdit()
        content.setToolTip(_("The content to paste"))
        content.setStyleSheet('color: {fg}; background-color: {bg}'.format(
            fg=settings['NewPasteWindow']['fgcolor'],
            bg=settings['NewPasteWindow']['bgcolor'],
        ))
        main_layout.addWidget(content)

        font = QFont()
        font.fromString(settings['NewPasteWindow']['font'])
        font.setStyleHint(QFont.Monospace)
        content.setFont(font)

        # 'Forms' in the middle.
        self._pastebin_combo = pastebin = QComboBox()
        self._expiry_combo = expiry = QComboBox()
        self._name_line_edit = name = QLineEdit()
        self._syntax_line_edit = syntax = QLineEdit()

        # This is not a form main_layout because it has four columns instead
        # of two.
        grid = QGridLayout()
        main_layout.addLayout(grid)

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

        # Progress bar and buttons.
        hbox = QHBoxLayout()
        main_layout.addLayout(hbox)

        progressbar = self._progressbar = QProgressBar()
        hbox.addWidget(progressbar)

        paste_button = QPushButton(_("Paste!"))
        paste_button.clicked.connect(self._paste)
        hbox.addWidget(paste_button)

        cancel_button = QPushButton(_("Cancel"))
        cancel_button.clicked.connect(self.close)
        hbox.addWidget(cancel_button)

    def _paste(self):
        """Start pasting."""
        self._progressbar.setRange(0, 0)  # Move back and forth.
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
        self._progressbar.setRange(0, 1)  # Stay at 0%.
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
        _new_paste_windows.remove(self)
        event.accept()


def new_paste():
    """Create a new paste."""
    window = _NewPasteWindow()
    window.setWindowTitle("New paste")
    window.resize(600, 400)
    window.show()
    _new_paste_windows.append(window)
