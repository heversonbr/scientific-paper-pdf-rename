#!/bin/bash

# Uploading the distribution archives to TestRegistry
# refs:  https://packaging.python.org/tutorials/packaging-projects/#uploading-the-distribution-archives
#
# The first thing you’ll need to do is register an account on TestPyPI, 
# which is a separate instance of the package index intended for testing and experimentation. 
# It’s great for things like this tutorial where we don’t necessarily want to upload to the real index. 
# To register an account, go to https://test.pypi.org/account/register/ and complete the steps on that page. 
# You will also need to verify your email address before you’re able to upload any packages. 
# For more details, see Using TestPyPI.

# To securely upload your project, you’ll need a PyPI API token.
# Create one at https://test.pypi.org/manage/account/#api-tokens, setting the “Scope” to “Entire account”. 
# Don’t close the page until you have copied and saved the token — you won’t see that token again.


#  registered, you can use twine to upload the distribution packages. You’ll need to install Twine:
python3 -m pip install --upgrade twine

# Once installed, run Twine to upload all of the archives under dist:
python3 -m twine upload --repository testpypi dist/*

# Once uploaded, your package should be viewable on TestPyPI; for example: 
#        https://test.pypi.org/project/example_package_YOUR_USERNAME_HERE.