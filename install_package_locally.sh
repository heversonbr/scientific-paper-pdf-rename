#!/bin/bash

echo "-------------------------------------"
pip uninstall sci-paper-rename
echo "-------------------------------------"
pip uninstall PyMuPDF
echo "-------------------------------------"
pip install .
echo "-------------------------------------"
echo "If success, now we can test our app locally" 
echo "-------------------------------------"
echo "Testing with: sci-paper-rename --help" 
echo "-------------------------------------"
sci-paper-rename --help