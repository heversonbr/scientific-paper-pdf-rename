#!/usr/bin/env python3

import sys
sys.path.append('../')
from sci_rename import move_file
import re


def move():
    
    src_file = 'teste.txt'
    dest_dir = "test_dir"
    move_file(src_file, dest_dir)
 

if __name__ == '__main__':
    
    move()