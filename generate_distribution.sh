#!/bin/bash

# venv
# python3 -m venv .venv 
# source .venv/bin/activate 
# pip list
# python3 -m pip install --upgrade pip
# pip list

# requirements
# Make sure you have the latest version of PyPA’s build installed
python3 -m pip install --upgrade build 

# Generating distribution archives
# Run this command from the same directory where pyproject.toml is located
# the '--sdist' option builds the 'source distribution'
# the '--wheel' option builds the 'built distribution'
# without any option it builds both
python3 -m build
# remind: there are 3 types of whell: universal wheel, pure-Python wheel and platform wheel 
# refs: https://realpython.com/python-wheels/


# This command should output a lot of text and once completed should generate two files in the dist directory:
# dist/
# ├── example_package_YOUR_USERNAME_HERE-0.0.1-py3-none-any.whl
# └── example_package_YOUR_USERNAME_HERE-0.0.1.tar.gz

# ref: https://realpython.com/pypi-publish-python-package/


