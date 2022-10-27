# -*- coding: utf-8 -*-


from setuptools import find_packages
from setuptools import setup

import fastentrypoints

dependencies = ["click"]

config = {
    "version": "0.1",
    "name": "click_auto_help",
    "url": "https://github.com/jakeogh/click-auto-help",
    "license": "ISC",
    "author": "Justin Keogh",
    "author_email": "github.com@v6y.net",
    "description": "print full --help when a incorrect command is used",
    "long_description": __doc__,
    "packages": find_packages(exclude=["tests"]),
    "package_data": {"click_auto_help": ["py.typed"]},
    "include_package_data": True,
    "zip_safe": False,
    "platforms": "any",
    "install_requires": dependencies,
}

setup(**config)
