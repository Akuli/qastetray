# Advanced QasteTray usage: Custom pastebin scripts

If QasteTray doesn't support your favorite pastebin by default and you
have some experience with programming in Python, you can write a
QasteTray plugin.

## Getting started

First you need to clone the QasteTray GitHub repository and see if
QasteTray can run from it:

```
git clone https://github.com/Akuli/qastetray/
cd qastetray
python3 -m qastetray
```

There should be some pastebin scripts in `qastetray/qastetray/pastebins`.
Your pastebin script should be there too. The filename must consist of
nothing but lowercase letters and underscores, but it must not start
with an underscore. It should also have a `.py` extension. If the
pastebin's filename is not correct it won't be used. In Python, you can
use a regular expression to check if the pastebin filename is correct:

```py
>>> import re
>>> bool(re.search(r'^[a-z][a-z_]*\.py$', 'my_pastebin.py'))
True
>>> bool(re.search(r'^[a-z][a-z_]*\.py$', '_this-Is-Not-A-Valid-Name.foobar'))
False
>>> 
```

## Example: hastebin script

The hastebin script in `qastetray/pastebins/hastebin.py` is one of the
shortest pastebin scripts QasteTray comes with.

```py
import requests

name = 'hastebin'
url = 'http://hastebin.com/'
expiry_days = [30]

paste_args = ['content']


def paste(content):
    """Make a paste to hastebin.com."""
    response = requests.post('http://hastebin.com/documents/',
                             data=content.encode('utf-8'))
    response.raise_for_status()
    return 'http://hastebin.com/' + response.json()['key']
```

Let's go through it and see how it works.

```py
import requests
```

The pastebin script is executed in Python with import, so you are free
to do anything you want in it. In this case, we're going to use requests
to do a HTTP post later, so we'll import it.

```py
name = 'hastebin'
url = 'http://hastebin.com/'
expiry_days = [30]
```

All QasteTray pastebins need a `name`, a `url` and an `expiry_days`. The
url should be something users can click to open the pastebin's official
website to make a paste theirselves or read the pastebin's terms and
conditions, and `expiry_days` should be a list of integers. A negative
value like -1 means that the paste will never expire. In this case, one
month is the only expiration hastebin allows so we set `expiry_days` to
a list with nothing but 30 in it.

```py
paste_args = ['content']


def paste(content):
    """Make a paste to hastebin.com."""
    response = requests.post('http://hastebin.com/documents/',
                             data=content.encode('utf-8'))
    response.raise_for_status()
    return 'http://hastebin.com/' + response.json()['key']
```

There must be a function called `paste` and it should make a paste,
raise an exception if it fails and return the URL the new paste ended up
in, which is exactly what this example is doing. The arguments (in this
case, only `content`) are given as keyword arguments, so
`def paste(content_to_paste)` would not work. You should also add a list
of arguments to `paste_args`.

## Example: dpaste script

The dpaste script in `qastetray/pastebins/dpaste.py` uses most of the
features available in QasteTray's pastebin scripts.

```py
import requests
from qastetray import USER_AGENT

name = 'dpaste'
url = 'http://dpaste.com/'
expiry_days = [1, 7, 30, 365]
syntax_default = 'Plain text'
syntax_choices = {
    # This was generated with scripts/syntax_getters/dpaste.py in the
    # QasteTray source package.
    "RHTML": "rhtml",
    "Io": "io",
    # (more lines)
    "Plain text": "text",
    # (more lines)
}

paste_args = ['content', 'expiry', 'syntax', 'title', 'username']


def paste(content, expiry, syntax, title, username):
    """Make a paste to dpaste.com."""
    response = requests.post(
        'http://dpaste.com/api/v2/',
        data={
            'content': content,
            'syntax': syntax,
            'title': title,
            'poster': username,
            'expiry_days': expiry,
        },
        headers={'User-Agent': USER_AGENT},
    )
    response.raise_for_status()
    return response.text.strip()
```

Many things here are similar with the hastebin script above, so let's go
through everything new.

```py
from qastetray import USER_AGENT
```

You can import QasteTray just like any other Python module. If you have
QasteTray installed, you can run Python, import it and check what you
can use from it:

```py
>>> import qastetray
>>> dir(qastetray)
['AUTHORS', 'DEBIAN_DEPENDS', 'GObject', 'KEYWORDS', 'LONG_DESC',
 'PIP_DEPENDS', 'SHORT_DESC', 'SHORT_DESC_TRANS', 'TRANSLATORS', 'URL',
 'USER_AGENT', 'VERSION', '_', '__builtins__', '__cached__', '__doc__',
 '__file__', '__loader__', '__name__', '__package__', '__path__',
 '__spec__', '__warningregistry__', '_get_translation', 'gettext', 'gi',
 'locale', 'resource_stream', 'signal']
>>> 
```

Usually you can use variables with UPPERCASE names. In this case we use
`USER_AGENT`, which is equivalent to `'QasteTray/' + VERSION`.

```py
syntax_default = 'Plain text'
syntax_choices = {
    # This was generated with scripts/syntax_getters/dpaste.py in the
    # QasteTray source package.
    "RHTML": "rhtml",
    "Io": "io",
    # (more lines)
    "Plain text": "text",
    # (more lines)
}
```

dpaste supports syntax highlighting, so it needs a default syntax and a
dictionary of possible syntax choices. In `syntax_choices`, the keys
will be the displayed names of the syntax highlightings and one of the
values will be given to the paste function. `syntax_default` is one of
`syntax_choices` keys and it will be selected by default. You should set
it to the pastebin's equivalent of plain text.

You don't have to copy-paste all syntax choices manually. I recommend
writing a script to download the syntax choice list for you. See
`scripts/syntax_getters` for examples.

```py
paste_args = ['content', 'expiry', 'syntax', 'title', 'username']


def paste(content, expiry, syntax, title, username):
    """Make a paste to dpaste.com."""
    response = requests.post(
        'http://dpaste.com/api/v2/',
        data={
            'content': content,
            'syntax': syntax,
            'title': title,
            'poster': username,
            'expiry_days': expiry,
        },
        headers={'User-Agent': USER_AGENT},
    )
    response.raise_for_status()
    return response.text.strip()
```

The paste function works much like before, but now we have more
paste_args. `expiry` will be an element of the `expiry_days` list,
`syntax` will be a value from `syntax_choices` and `title` and
`username` will be a string the user has entered.

## Sharing your pastebin script

If you've written a pastebin script for QasteTray you can fork
[my QasteTray repository](https://github.com/Akuli/qastetray), add your
script to your fork and make a pull request. I'd be happy to support
more pastebins by default, and if I decide to add your pastebin script
you'll find your name or nick from the author list.
