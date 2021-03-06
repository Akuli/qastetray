#!/usr/bin/env python3

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

"""Convert and move files.

Running this file will make HTML documentation for QasteTray from
markdown files, copy and resize icons and convert .po files to .mo files
using msgfmt.
"""

import os
import shutil
import subprocess
import sys

import markdown
from pygments.formatters import HtmlFormatter


CSS_TEMPLATE = """\
/* This file is used as a style file for QasteTray HTML documentation. */

body {
    background: #C38000;
}

div {
    border-radius: 10px;
    background: white;
    margin: 10px;
    padding: 10px;
}

/*table, th, td {
    border: 1px solid black;
    border-radius: 5px;
}*/


/* The codehilite color rules will be added here: */
"""

HTML_TEMPLATE = """\
<!-- This file is automatically generated QasteTray HTML documentation. -->

<!DOCTYPE html>

<html>

<head>
<title>{title}</title>
<meta charset="utf-8">
<link rel="stylesheet" type="text/css" href="style.css">
<link rel="icon" href="icon.png">
</head>

<body>
<div id="content">
{content}
</div>
</body>

</html>
"""


def _fix_codeblocks(md):
    """Change ``` code blocks to indented code blocks."""
    languages = {'py': 'python', '': 'sh'}
    lines = iter(md.split('\n'))
    content = ''

    try:
        while True:
            line = next(lines)
            if line.startswith('```'):
                # Code, this must be indented.
                lang = languages[line[3:].strip()]
                content += '    :::{}\n'.format(lang)
                while True:
                    line = next(lines)
                    if line.rstrip() == '```':
                        break
                    content += '    {}\n'.format(line)
            else:
                content += '{}\n'.format(line)
    except StopIteration:
        return content


def _fix_links(md):
    """Change links in markdown to make them work in HTML."""
    md = md.replace('(doc/', '(')
    md = md.replace('.md)', '.html)')
    return md


def _make_html(md):
    """Convert markdown to HTML."""
    title = md.split('\n', 1)[0].lstrip('# ')
    md = _fix_codeblocks(md)
    md = _fix_links(md)
    content = markdown.markdown(md, extensions=['codehilite'])
    return HTML_TEMPLATE.format(title=title, content=content)


def _make_css():
    """Return the content of a style.css file."""
    formatter = HtmlFormatter(style='tango')
    return CSS_TEMPLATE + formatter.get_style_defs('.codehilite')


def convert_docs():
    """Convert markdown documentation to HTML documentation.

    The resize_icons function must be called before this.
    """
    # HTML files.
    files = [('README.md', 'index.html'),
             ('writing-pastebins.md', 'writing-pastebins.html')]
    for src, dst in files:
        with open(src, 'r') as f:
            md = f.read()
        html = _make_html(md)
        with open(os.path.join('doc', dst), 'w') as f:
            f.write(html)

    # CSS file.
    css = _make_css()
    with open(os.path.join('doc', 'style.css'), 'w') as f:
        f.write(css)

    # LICENSE file.
    shutil.copy('LICENSE', os.path.join('doc', 'LICENSE'))

    # Icon.
    shutil.copy(os.path.join('icons', 'hicolor', '16x16',
                             'apps', 'qastetray.png'),
                os.path.join('doc', 'icon.png'))


def _resize_icon(big):
    """Create small icons from a big 256x256px icon."""
    for size in (16, 22, 24, 32, 48, 64, 128):
        size = '{0}x{0}'.format(size)
        # TODO: Replace this with something better.
        small = big.replace('256x256', size)
        os.makedirs(os.path.dirname(small), exist_ok=True)
        shutil.copy(big, small)
        subprocess.check_call(['mogrify', '-resize', size, small])


def resize_icons():
    """Create small icons from 256x256 icons.

    TODO: Support more icons than qastetray.png.
    """
    for theme in os.listdir('icons'):
        big_icon_dir = os.path.join('icons', theme, '256x256')
        if not os.path.isdir(big_icon_dir):
            continue
        for root, dirs, files in os.walk(big_icon_dir):
            for f in files:
                _resize_icon(os.path.join(root, f))


def run_msgfmt():
    """Convert .po files to .mo files."""
    for language in os.listdir('locale'):
        msgdir = os.path.join('locale', language, 'LC_MESSAGES')
        if not os.path.isfile(os.path.join(msgdir, 'qastetray.po')):
            continue
        subprocess.check_call(['msgfmt', os.path.join(msgdir, 'qastetray.po'),
                               '-o', os.path.join(msgdir, 'qastetray.mo')])


def main():
    """Run other 'compiling' functions."""
    resize_icons()
    convert_docs()
    run_msgfmt()


if __name__ == '__main__':
    main()
    print("Compiling succeeded.")
    print("Now you can run '{} -m qastetray'.".format(sys.executable))
