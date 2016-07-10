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

from qastetray import settings


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

        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        form = self._make_form_in_groupbox(_("New paste window"))

        combo = QtWidgets.QComboBox()
        for index, (name, value) in enumerate(_wrap_modes):
            combo.addItem(name)
            if value == settings.get_str('NewPasteWindow', 'wrap'):
                combo.setCurrentIndex(index)
        combo.currentIndexChanged.connect(self._wrap_changed)
        form.addRow(_("Text wrapping:"), combo)

        button = _FontButton(settings.get_str('NewPasteWindow', 'font'))
        button.selection_changed.connect(self._font_changed)
        form.addRow(_("Font:"), button)

        button = _ColorButton(settings.get_str('NewPasteWindow', 'fgcolor'))
        button.selection_changed.connect(self._fg_changed)
        form.addRow(_("Foreground color:"), button)

        button = _ColorButton(settings.get_str('NewPasteWindow', 'bgcolor'))
        button.selection_changed.connect(self._bg_changed)
        form.addRow(_("Background color"), button)

    def _make_form_in_groupbox(self, label):
        """Create and return a QFormLayout in a QGroupBox.

        The group box is added to self.layout.
        """
        group = QtWidgets.QGroupBox()
        self.layout().addWidget(group)
        form = QtWidgets.QFormLayout()
        group.setLayout(form)
        return form

    def _wrap_changed(self, index):
        """Change wrap mode."""
        settings.set_str('NewPasteWindow', 'wrap', _wrap_modes[index][1])

    def _font_changed(self, font_name):
        """Change font."""
        settings.set_str('NewPasteWindow', 'font', font_name)

    def _fg_changed(self, color_name):
        """Change foreground color."""
        settings.set_str('NewPasteWindow', 'fgcolor', color_name)

    def _bg_changed(self, color_name):
        """Change background color."""
        settings.set_str('NewPasteWindow', 'bgcolor', color_name)


def run():
    """Run the setting dialog."""
    global _dialog      # Avoid garbage collection
    _dialog = _SettingDialog()
    _dialog.setWindowTitle(_("QasteTray preferences"))
    _dialog.resize(600, 400)
    _dialog.show()
