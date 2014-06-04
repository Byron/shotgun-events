#!/usr/bin/env python
from setuptools import setup, find_packages

pkg_root = 'src/python'

setup(name='shotgun-events',
      version='0.1.0',
      description='Poll shotgun events and dispatch them to plugins',
      author='Sebastian Thiel',
      author_email='byronimo@gmail.com',
      url='https://github.com/Byron/shotgun-events',
      packages=find_packages(pkg_root),
      package_dir={'' : pkg_root},
     )
