#!/bin/bash

# Requirements
echo "-----------------------------------------------------------------"
python3 -m pip install --upgrade pip
echo "-----------------------------------------------------------------"
python3 -m pip install --upgrade build
echo "-----------------------------------------------------------------"


# Generating distribution archives
# the '--sdist' option builds the 'source distribution'
# the '--wheel' option builds the 'built distribution'
# without any option it builds both
python3 -m build
echo "-----------------------------------------------------------------"
# remind: there are 3 types of whell: universal wheel, pure-Python wheel and platform wheel 
# refs: https://realpython.com/python-wheels/

# Uploading the distribution archives 
#refs:  https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives
python3 -m pip install --upgrade twine
#python3 -m twine upload --repository testpypi dist/*


#other refs: https://realpython.com/pypi-publish-python-package/