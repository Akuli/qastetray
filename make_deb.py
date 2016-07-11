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

"""Create a QasteTray Debian package."""


import os
import math
import shutil
import subprocess
import sys
import textwrap

import compiler
import qastetray


def check_platform():
    """Make sure the platform can be used for building the package.

    Exit with an error message if a problem is detected.
    """
    if os.getcwd() != os.path.dirname(os.path.abspath(__file__)):
        error = "must be ran in the directory it's located at"
    if os.path.sep != '/':
        error = "a unix-like operating system is required"
    elif not shutil.which('dpkg-deb'):
        error = "cannot find dpkg-deb"
    elif os.getuid() != 0:
        error = "must be ran as root (or with fakeroot)"
    else:
        return
    sys.exit("{}: error: {}".format(sys.argv[0], error))


def copy_files():
    """Copy files for building."""
    os.makedirs('build/usr/lib/python3/dist-packages', exist_ok=True)
    os.makedirs('build/usr/share/doc', exist_ok=True)

    shutil.copytree('applications', 'build/usr/share/applications')
    shutil.copytree('doc', 'build/usr/share/doc/qastetray')
    shutil.copytree('icons', 'build/usr/share/icons')
    shutil.copytree('locale', 'build/usr/share/locale')
    shutil.copytree('qastetray',
                    'build/usr/lib/python3/dist-packages/qastetray')


def clean():
    for root, dirs, files in os.walk('build'):
        # Remove Python cache directories
        for d in dirs:
            if d == '__pycache__':
                shutil.rmtree(os.path.join(root, d))

        # Remove .po files
        for f in files:
            if f.endswith('.po'):
                os.remove(os.path.join(root, f))


def create_dirsconf():
    """Create a dirs.conf for QasteTray."""
    data = textwrap.dedent('''\
    [InstallDirs]
    docdir = /usr/share/doc/qastetray
    icondir = /usr/share/icons
    localedir = /usr/share/locale
    ''')
    with open('build/usr/lib/python3/dist-packages/'
              'qastetray/dirs.conf', 'w') as f:
        f.write(data)


def create_launcher():
    """Create a qastetray file to bin."""
    data = textwrap.dedent('''\
    #!/usr/bin/env python3

    """QasteTray launcher."""


    from qastetray.__main__ import main

    if __name__ == '__main__':
        main()
    ''')
    with open('build/usr/bin/qastetray', 'w') as f:
        f.write(data)


def _get_dir_size(directory):
    """Return the size of a directory.

    This is recursive.
    """
    size = os.path.getsize(directory)
    for item in os.listdir(directory):
        item = os.path.join(directory, item)
        if os.path.isfile(item):
            size += os.path.getsize(item)
        elif os.path.isdir(item):
            size += _get_dir_size(item)
    return size


def create_control():
    """Create a control file."""
    os.makedirs('build/DEBIAN', exist_ok=True)

    # The description needs to be formatted in a special way.
    description = ''
    for line in textwrap.wrap(qastetray.LONG_DESC, 71):
        description += ' '
        if line:
            description += line
        else:
            description += '.'
        description += '\n'

    data = textwrap.dedent('''\
    Package: qastetray
    Priority: extra
    Section: net
    Installed-Size: {size}
    Maintainer: {maintainer}
    Architecture: all
    Version: {version}
    Depends: {depends}
    Description: {short_desc}
    {long_desc}
    ''')
    data = data.format(
        size=math.ceil(_get_dir_size('build') / 1024),
        maintainer=qastetray.MAINTAINER,
        version=qastetray.VERSION,
        depends=', '.join(qastetray.DEBIAN_DEPENDS),
        short_desc=qastetray.SHORT_DESC.rstrip('.'),
        long_desc=description,
    )
    with open('build/DEBIAN/control', 'w') as f:
        f.write(data)


def fix_permissions():
    """Change permissions of files."""
    for root, dirs, files in os.walk('build'):
        for d in dirs:
            os.chmod(os.path.join(root, d), 0o755)
        for f in files:
            os.chmod(os.path.join(root, f), 0o644)

    # The executable must be executable.
    os.chmod('build/usr/bin/qastetray', 0o755)


def build_deb():
    """Build a Debian package with dpkg-deb."""
    subprocess.check_call(['dpkg-deb', '--build', 'build', 'qastetray.deb'],
                          stdout=subprocess.DEVNULL)


def main():
    """Build the package."""
    if os.path.isdir('build'):
        shutil.rmtree('build')

    check_platform()
    compiler.main()
    copy_files()
    clean()
    create_dirsconf()
    create_control()
    build_deb()


if __name__ == '__main__':
    main()
    print("Building the package succeeded.")
    print("Now you can install qastetray.deb.")
