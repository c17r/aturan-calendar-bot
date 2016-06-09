#!/usr/bin/env python

from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='aturan-calendar-bot',
    version='0.1.0',
    description='Once a day twitter bot, sharing the Aturan Date',
    long_description=long_description,
    url='https://github.com/c17r/aturan-calendar-bot',
    author='Christian Sauer',
    author_email='sauerc@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
    ],
    py_modules=[
        'aturan_calendar_bot',
    ],
    install_requires=[
        'arrow<0.8.0',
        'twitter<1.18.0',
        'voluptuous<0.9.0',
        'aturan-calendar',
    ],
    tests_require=[
        'pytest',
        'pytest-conv',
        'pytest-mock',
    ],
    dependency_links=[
        'https://github.com/c17r/aturan-calendar/archive/v0.3.0.zip#egg=aturan-calendar-0.3.0',
    ],
    entry_points={
        'console_scripts': [
            'aturan-calendar-bot = aturan_calendar_bot:main',
        ],
    },
)
