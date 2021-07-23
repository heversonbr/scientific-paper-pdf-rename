#!/bin/bash

# Requirements
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade build

# Generating distribution archives
python3 -m build


# Uploading the distribution archives 
# https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives

#python3 -m pip install --upgrade twine

#python3 -m twine upload --repository testpypi dist/*

