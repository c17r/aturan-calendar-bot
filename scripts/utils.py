import os
import re
import sys
from importlib import import_module


_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SRC = os.path.join(_ROOT, 'src')


def make_readme(name, repo):
    readme = os.path.join(_ROOT, 'README.rst')
    with open(readme, 'w') as f:
        f.write('''.. start-badges

.. list-table::
    :stub-columns: 1

    * - tests
      - |coveralls|
    * - package
      - |travis|

.. |travis| image:: https://travis-ci.org/{name}/{repo}.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/{name}/{repo}

.. |coveralls| image:: https://coveralls.io/repos/github/{name}/{repo}/badge.svg?branch=master
    :alt: Coverage Status
    :target: https://coveralls.io/github/{name}/{repo}

.. end-badges
'''.format(name=name, repo=repo))

        for doc in _get_modules():
            f.write(doc)
            f.write('')


def make_long_description():
    return '\n'.join((doc for doc in _get_modules()))


def _get_modules():
    _, folders, _ = next(os.walk(_SRC))
    for folder in folders:
        if 'egg-info' in folder:
            continue
        rv = get_module_string(folder)
        if rv:
            yield rv


def get_module_string(name):
    init = os.path.join(_SRC, name, '__init__.py')
    try:
        with open(init, mode='r', encoding='utf-8') as f:
            data = f.read()
        return re.search('\A"""(.*)"""', data, flags=re.S | re.M).group(1)
    except:
        return None


def _get_setup():
    sys.path.insert(0, _ROOT)
    mod = import_module('setup')
    return mod
