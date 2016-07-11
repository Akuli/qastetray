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

"""Setting changing dialog."""

from gettext import gettext as _
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialogButtonBox, QPushButton

from qastetray.settings import settings


class _ColorButton(QtWidgets.QPushButton):
    """Button for choosing a color."""

    selection_changed = QtCore.pyqtSignal(str)

    def __init__(self, color_name, *args, **kwargs):
        """Initialize the color button."""
        super().__init__(*args, **kwargs)
        self.clicked.connect(self._on_click)
        self.set_color_name(color_name)

    def set_color_name(self, color_name):
        """Set the color name."""
        self.setStyleSheet('background-color: ' + color_name)
        self._color_name = color_name

    def get_color_name(self):
        """Get the color name."""
        return self._color_name

    def _on_click(self):
        """Get a new color from the user."""
        orig_qcolor = QtGui.QColor(self.get_color_name())
        new_qcolor = QtWidgets.QColorDialog.getColor(orig_qcolor, self)
        if new_qcolor.isValid():
            new_color_name = new_qcolor.name()
            self.set_color_name(new_color_name)
            self.selection_changed.emit(new_color_name)


class _FontButton(QtWidgets.QPushButton):
    """Button for choosing a font."""

    selection_changed = QtCore.pyqtSignal(str)

    def __init__(self, font_string, *args, **kwargs):
        """Initialize the font button."""
        super().__init__(*args, **kwargs)
        self.clicked.connect(self._on_click)
        self.set_font_string(font_string)

    def set_font_string(self, font):
        """Set the font string."""
        qfont = QtGui.QFont()
        qfont.fromString(font)
        self.setFont(qfont)
        self.setText('{} {}'.format(qfont.family(), qfont.pointSize()))

    def get_font_string(self):
        """Get the font string."""
        return self.font().toString()

    def _on_click(self):
        """Get a new font from the user."""
        font, ok = QtWidgets.QFontDialog.getFont(self.font(), self)
        if ok:
            font = font.toString()
            self.set_font_string(font)
            self.selection_changed.emit(font)


_wrap_modes = (
    # [text, QTextOption attribute],
    [_("No wrapping"), 'NoWrap'],
    [_("Words"), 'WordWrap'],
    [_("Characters"), 'WrapAnywhere'],
    [_("Words and characters"), 'WrapAtWordBoundaryOrAnywhere'],
)


class _SettingDialog(QtWidgets.QDialog):
    """Dialog for changing settings."""

    def __init__(self):
        """Initialize the setting dialog."""
        super().__init__()
        self.setWindowTitle("QasteTray settings")

        main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(main_layout)

        form = self._make_form_in_group(_("New paste window"))

        names, attrs = zip(*_wrap_modes)
        attr = settings['NewPasteWindow']['wrap']
        self._wrap_combo = QtWidgets.QComboBox()
        self._wrap_combo.addItems(names)
        self._wrap_combo.setCurrentIndex(attrs.index(attr))
        form.addRow(_("Text wrapping:"), self._wrap_combo)

        self._font_button = _FontButton(settings['NewPasteWindow']['font'])
        form.addRow(_("Font:"), self._font_button)

        self._fg_button = _ColorButton(settings['NewPasteWindow']['fgcolor'])
        form.addRow(_("Foreground color:"), self._fg_button)

        self._bg_button = _ColorButton(settings['NewPasteWindow']['bgcolor'])
        form.addRow(_("Background color:"), self._bg_button)

        main_layout.addStretch(1)

        buttonbox = QDialogButtonBox()
        main_layout.addWidget(buttonbox)

        apply_button = QPushButton(_("&Apply"))
        apply_button.clicked.connect(self._apply)
        buttonbox.addButton(apply_button, QDialogButtonBox.ApplyRole)

        ok_button = QPushButton("&OK")
        ok_button.clicked.connect(self._ok)
        buttonbox.addButton(ok_button, QDialogButtonBox.AcceptRole)

        cancel_button = QPushButton(_("&Cancel"))
        cancel_button.clicked.connect(self.close)
        buttonbox.addButton(cancel_button, QDialogButtonBox.RejectRole)

    def _make_form_in_group(self, label_text):
        """Create and return a QFormLayout in a QGroupBox.

        The group box is added to the main main_layout.
        """
        group = QtWidgets.QGroupBox(label_text)
        self.layout().addWidget(group)
        form = QtWidgets.QFormLayout()
        group.setLayout(form)
        return form

    def _ok(self):
        """Save the settings and close the dialog."""
        self._apply()
        self.close()

    def _apply(self):
        """Save the settings."""
        font = self._font_button.get_font_string()
        fg = self._fg_button.get_color_name()
        bg = self._bg_button.get_color_name()
        settings['NewPasteWindow']['font'] = font
        settings['NewPasteWindow']['fg'] = fg
        settings['NewPasteWindow']['bg'] = bg


def run():
    """Run the setting dialog."""
    global _dialog      # Avoid garbage collection
    _dialog = _SettingDialog()
    _dialog.setWindowTitle(_("QasteTray preferences"))
    _dialog.resize(400, 300)
    _dialog.show()
