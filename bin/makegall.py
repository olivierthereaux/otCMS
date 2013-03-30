#!/usr/bin/env python
# encoding: utf-8
"""
makegall.py

Find jpg fnames in current dir and output basic gallery markup

Created by Olivier Thereaux on 2012-07-11.
"""

import sys
import os
import re

def readRDF(fname):
    """Yes, this is how I parse my PhotoRDF. Sue me."""
    try:
        rdf = open(fname, "r").read()
    except Exception, e:
        raise e
        return "", ""
    title = ''
    description = ''
    try:
        title = re.search(r'<s0:title>(.*)</s0:title>', rdf).group(1)
    except Exception, e:
        pass
    try:
        description = re.search(r'<s0:description>(.*)</s0:description>', rdf).group(1)
    except:
        pass
    return title, description
    

def main():
    print '<div class="gall">'
    dirList=os.listdir(".")
    for fname in dirList:
        if re.search(r".jpg$", fname):
            file_base = re.sub(r"\..*$", "", fname)
            alt_text = ''
            link_text = ''
            title_text = ''
            rdf_fname = file_base+".rdf"
            if rdf_fname in dirList:
                title, description = readRDF(rdf_fname)
                alt_text = "Photo: "+title
                title_text = description
                link_text = title
            print '''<div class="gallone"><a href="%(fname)s.html" title=""><img src="tn/tn_%(fname)s.jpg" alt="%(alt_text)s" title="%(title_text)s" /></a><p><a href="%(fname)s.html">%(link_text)s</a></p></div>''' % {"fname": fname, 'alt_text': alt_text, "link_text": link_text, "title_text": title_text}
    print '</div>'

if __name__ == '__main__':
    main()
