#!/usr/bin/env python3

import sys
sys.path.append('../')
from sci_rename import parse_title
import re


def test_parse():
    
    title = 'This is* what_2 ? 1 example_  of !@#$%^&*()_+=-[]\|}{\'/?..><,``~~";}   How-to -  Describe - Find / : etc' 
    print('title: ' + title)
    print('parsed title: ' + parse_title(title))

if __name__ == '__main__':
    
    test_parse()