#!/usr/bin/env python
# -*- coding: utf-8 -*-

import glob
import os
import re

from distribute_setup import use_setuptools; use_setuptools()
from setuptools import setup, find_packages


rel_file = lambda *args: os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)

def read_from(filename):
    fp = open(filename)
    try:
        return fp.read()
    finally:
        fp.close()

def lines_from(filename):
    return filter(None, map(lambda s: s.strip(), read_from(filename).splitlines()))

def get_version():
    data = read_from(rel_file('src', 'dagny', '__init__.py'))
    return re.search(r"__version__ = '([^']+)'", data).group(1)

def get_requirements():
    return lines_from(rel_file('REQUIREMENTS'))

def get_extra_requirements():
    extras_require = {}
    for req_filename in glob.glob(rel_file('REQUIREMENTS.*')):
        group = os.path.basename(req_filename).split('.', 1)[1]
        extras_require[group] = lines_from(req_filename)
    return extras_require


setup(
    name             = 'dagny',
    version          = get_version(),
    author           = "Zachary Voase",
    author_email     = "z@zacharyvoase.com",
    url              = 'http://github.com/zacharyvoase/dagny',
    description      = "Rails-style Resource-Oriented Architecture for Django.",
    packages         = find_packages(where='src'),
    package_dir      = {'': 'src'},
    install_requires = get_requirements(),
    extras_require   = get_extra_requirements(),
)
