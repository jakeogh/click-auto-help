# -*- coding: utf-8 -*-

import sys
import fastentrypoints
from setuptools import find_packages, setup
if not sys.version_info[0] == 3:
    sys.exit("Python 3 is required. Use: \'python3 setup.py install\'")

dependencies = ["icecream", "click"]

config = {
    "version": "0.1",
    "name": "click_auto_help",
    "url": "https://github.com/jakeogh/click-auto-help",
    "license": "ISC",
    "author": "Justin Keogh",
    "author_email": "github.com@v6y.net",
    "description": "print full --help when a incorrect command is used",
    "long_description": __doc__,
    "packages": find_packages(exclude=['tests']),
    "package_data": {"click_auto_help": ['py.typed']},
    "include_package_data": True,
    "zip_safe": False,
    "platforms": "any",
    "install_requires": dependencies,
    "entry_points": {
        "console_scripts": [
            "click-auto-help=click_auto_help.click_auto_help:cli",
        ],
    },
}

setup(**config)