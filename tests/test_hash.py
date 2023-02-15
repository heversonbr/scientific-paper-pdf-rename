#!/usr/bin/env python3

import sys
sys.path.append('../')
from sci_rename import hash_file
import re

def test_hash():
    file1 = '../examples/1.pdf'
    file2 = '../examples/1.pdf'
    file3 = '../examples/2.pdf'
    
    print(hash_file(file1))
    print(hash_file(file2))
    print(hash_file(file3))

if __name__ == '__main__':
    
    test_hash()