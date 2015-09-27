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
import getopt

help_message = '''
makegall.py - Find jpg fnames in current dir and output basic gallery markup

Options:
    --inline    output markup to display images in the post
                (default is to have thumbnails)
    -h          this help message
'''


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
    try:
        coverage = re.search(r'<s0:coverage>(.*)</s0:coverage>', rdf).group(1)
    except:
        pass
    if description == coverage:
        description = title + u" – "+coverage
    try:
        date = re.search(r'<s0:date>(.*)</s0:date>', rdf).group(1)
        description = description + ", " + date
    except:
        pass
    return title, description


def main(argv=None):
    inline = False
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help", "inline"])
        except getopt.error, msg:
            raise Usage(msg)

        # option processing
        for option, value in opts:
            if option == "--inline":
                inline = True
            if option in ("-h", "--help"):
                raise Usage(help_message)

    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2

    if inline:
        template_markup = '''<div class="picCenter picCaption">
    <a href="%(fname)s" class="fresco" data-fresco-caption="%(title_text)s"><img src="%(fname)s" alt="%(alt_text)s" title="%(link_text)s" /></a>
    <p><a href="%(fname)s" class="fresco" data-fresco-caption="%(title_text)s">%(title_text)s</a></p>
</div>'''
    else:
        print '<div class="gall">'
        template_markup =  '''  <div class="gallone">
        <a href="%(fname)s" class="fresco"
        data-fresco-group="gall"
        data-fresco-group-options="ui: 'inside', thumbnails: 'vertical'"
        data-fresco-caption="%(title_text)s"
        title="%(title_text)s"
        data-fresco-options="thumbnail: 'tn/tn_%(fname)s.jpg'">
            <img src="tn/tn_%(fname)s.jpg" alt="%(alt_text)s"  />
        </a>
        <p><a href="%(fname)s" class="fresco"
        data-fresco-group="gall_text" >%(link_text)s</a></p>
    </div>'''
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
            print template_markup % {"fname": fname, 'alt_text': alt_text, "link_text": link_text, "title_text": title_text}
    if not inline:
        print '</div>'

if __name__ == '__main__':
    main()
