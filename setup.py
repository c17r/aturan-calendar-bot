#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: To use the 'upload' functionality of this file, you must:
#   $ pip install twine
import os
import sys
from shutil import rmtree
from os.path import basename
from os.path import splitext
from glob import glob

from setuptools import find_packages, setup, Command

from scripts.utils import make_long_description


# Package meta-data.
NAME = 'aturan-calendar-bot'
DESCRIPTION = 'Once a day twitter bot, sharing the Aturan Date'
REPO_USERNAME = 'c17r'
EMAIL = 'sauerc@gmail.com'
AUTHOR = 'Christian Sauer'
URL = 'https://github.com/{0}/{1}'.format(REPO_USERNAME, NAME)

# What packages are required for this module to be executed?
REQUIRED = [
    'aturan-calendar',
    'logbook',
    'arrow',
    'twitter<1.18.0',
    'voluptuous<0.9.0',
    'raven',
]

# The rest you shouldn't have to touch too much :)
# ------------------------------------------------
# Except, perhaps the License and Trove Classifiers!
# If you do change the License, remember to change the Trove Classifier for that!

PKG_NAME = NAME.replace('-', '_')

here = os.path.abspath(os.path.dirname(__file__))

long_description = make_long_description()

# Load the package's __version__.py module as a dictionary.
about = {}
with open(os.path.join(here, 'src', PKG_NAME, '__version__.py')) as f:
    exec(f.read(), about)


class UploadCommand(Command):
    """Support setup.py upload."""

    description = 'Build and publish the package.'
    repo = None
    user_options = []

    @staticmethod
    def status(s):
        """Prints things in bold."""
        print('\033[1m{0}\033[0m'.format(s))

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        try:
            self.status('Removing previous builds…')
            rmtree(os.path.join(here, 'dist'))
        except OSError:
            pass

        self.status('Building Source and Wheel (universal) distribution…')
        os.system('{0} setup.py sdist bdist_wheel --universal'.format(sys.executable))

        self.status('Uploading the package to PyPi via Twine…')
        self.repo = '--repository {}'.format(self.repo) if self.repo else ''
        cmd = 'twine upload {} dist/*'.format(self.repo)
        os.system(cmd)

        sys.exit()


class TestUploadCommand(UploadCommand):
    repo = 'testpypi'


# Where the magic happens:
if __name__ == '__main__':
    setup(
        name=NAME,
        version=about['__version__'],
        description=DESCRIPTION,
        long_description=long_description,
        author=AUTHOR,
        author_email=EMAIL,
        url=URL,
        packages=find_packages('src'),
        package_dir={'': 'src'},
        py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
        # If your package is a single module, use this instead of 'packages':
        # py_modules=['mypackage'],

        entry_points={
            'console_scripts': ['aturan-calendar-bot=aturan_calendar_bot:main'],
        },
        install_requires=REQUIRED,
        include_package_data=True,
        license='MIT',
        classifiers=[
            # Trove classifiers
            # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy'
        ],
        # $ setup.py publish support.
        cmdclass={
            'upload': UploadCommand,
            'test_upload': TestUploadCommand,
        },
    )
