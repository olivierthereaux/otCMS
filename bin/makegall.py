#!/usr/bin/env python
# encoding: utf-8
"""
makegall.py

Find jpg files in current dir and output basic gallery markup

Created by Olivier Thereaux on 2012-07-11.
"""

import sys
import os
import re

def main():
    print '<div class="gall">'
    dirList=os.listdir(".")
    for fname in dirList:
        if re.search(r".jpg$", fname):
            print '''<div class="gallone">
            <a href="%(file)s.html" title=""><img src="tn/tn_%(file)s.jpg" alt=""  /></a>
            <p><a href="%(file)s.html"></a></p>
            </div>
            ''' % {"file": fname}
    print '</div>'

if __name__ == '__main__':
    main()
