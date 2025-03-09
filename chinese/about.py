# Copyright © 2017-2018 Joseph Lorimer <joseph@lorimer.me>
#
# This file is part of Chinese Support 3.
#
# Chinese Support 3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# Chinese Support 3 is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Chinese Support 3.  If not, see <https://www.gnu.org/licenses/>.

from aqt import mw
from aqt.qt import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from ._version import __version__


CSR_GITHUB_URL = 'https://github.com/Gustaf-C/anki-chinese-support-3'
FORK_URL = 'https://github.com/leonbjorklund/anki-chinese-support-3'


def showAbout():
    dialog = QDialog(mw)

    label = QLabel()
    label.setStyleSheet('QLabel { font-size: 14px; }')

    text = '''
<div style="font-weight: bold">Chinese Support 3 v%s</div><br>
<div><span style="font-weight: bold">Original</span>: <a href="%s">%s</a></div>
<div><span style="font-weight: bold">Fork</span>: <a href="%s">%s</a></div>
<div>Implements own TTS method for higher quality audio (requires Google Cloud TTS setup)</div>
''' % (__version__, CSR_GITHUB_URL, CSR_GITHUB_URL, FORK_URL, FORK_URL)

    label.setText(text)
    label.setOpenExternalLinks(True)

    buttonBox = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
    buttonBox.accepted.connect(dialog.accept)

    layout = QVBoxLayout()
    layout.addWidget(label)
    layout.addWidget(buttonBox)

    dialog.setLayout(layout)
    dialog.setWindowTitle('About')
    dialog.exec()
