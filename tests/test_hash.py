#!/usr/bin/env python3

import sys
sys.path.append('../src/sci_paper_renamer/')
from sci_renamer import *
import re

def test_hash():
    file1 = '../examples/Benchmarking_Personal_Cloud_Storage.pdf'
    file2 = '../examples/Benchmarking_Personal_Cloud_Storage.pdf'
    file3 = '../examples/Blockchain_Consensus_Protocols_In_The_Wild.pdf'
    
    print(hash_file(file1))
    print(hash_file(file2))
    print(hash_file(file3))

if __name__ == '__main__':
    
    test_hash()