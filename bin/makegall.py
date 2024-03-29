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
    --inline  output markup to display images in the post
    --thumb   output markup to display gallery of thumbnails
    --lazy    output markup to display images in the post, with lazy load
              (default is --inline)
    -h        this help message
'''

def getImageSizes(fname):
    """calculate actual and relative dimensions of image"""
    sizes = dict()
    from PIL import Image
    im=Image.open(fname)
    (sizes["width"], sizes["height"]) = im.size
    if sizes["width"] >= sizes["height"]:
        sizes["rel_width"] = 600
        try:
            sizes["rel_height"] = int((float(sizes["height"])*float(sizes["rel_width"]))/float(sizes["width"]))
        except Exception as e:
            raise e
    else:
        sizes["rel_height"] = 600
        try:
            sizes["rel_width"] = int((float(sizes["width"])*float(sizes["rel_height"]))/float(sizes["height"]))
        except Exception as e:
            raise e

    return sizes


def readRDF(fname):
    """Yes, this is how I parse my PhotoRDF. Sue me."""
    try:
        rdf = open(fname, "r").read()
    except Exception as e:
        raise e
        return "", ""
    title = ''
    description = ''
    coverage = ''
    try:
        title = re.search(r'<s[0-9]:title>(.*)</s[0-9]:title>', rdf).group(1)
    except Exception as e:
        pass
    try:
        description = re.search(r'<s[0-9]:description>(.*)</s[0-9]:description>', rdf).group(1)
    except:
        pass
    try:
        coverage = re.search(r'<s[0-9]:coverage>(.*)</s[0-9]:coverage>', rdf).group(1)
    except:
        pass
    if description == coverage:
        description = title + " – "+coverage
    try:
        date = re.search(r'<s0:date>(.*)</s0:date>', rdf).group(1)
        description = description + ", " + date
    except:
        pass
    return title, description


def main(argv=None):
    mode = "inline" # default
    inline = False
    inline_lazy = False
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "h", ["help", "thumb", "inline", "lazy"])
        except getopt.error as msg:
            raise RuntimeError(msg)

        # option processing
        for option, value in opts:
            if option == "--inline":
                mode = "inline"
            if option == "--lazy":
                mode = "lazy"
            if option == "--thumb":
                mode = "thumb"
            if option in ("-h", "--help"):
                print(help_message)
                sys.exit()

    except AssertionError as err:
        print(sys.argv[0].split("/")[-1] + ": " + str(err.msg), file=sys.stderr)
        print("\t for help use --help", file=sys.stderr)
        return 2

    if mode=="inline-nojs":
        template_markup = '''<div class="picCenter picCaption">
  <a href="#img%(fname)s"><img src="%(fname)s" class="thumbnail" alt="%(alt_text)s" title="%(link_text)s"></a>
  <p>%(title_text)s</p>
  <a href="#_" class="lightbox" id="img%(fname)s"><img src="%(fname)s"></a>
</div>'''
    elif mode=="inline":
        template_markup = '''<div class="picCenter picCaption">
    <a href="%(fname)s" class="fresco" data-fresco-group="inline" data-fresco-group-options="ui: 'inside', thumbnails: 'vertical'" data-fresco-caption="%(title_text)s"><img src="%(fname)s" alt="%(alt_text)s" title="%(link_text)s" /></a>
    <p><a href="%(fname)s" class="fresco" data-fresco-group="inline-text" data-fresco-group-options="ui: 'inside', thumbnails: 'vertical'" data-fresco-caption="%(title_text)s">%(title_text)s</a></p>
</div>'''
    elif mode =="lazy":
        template_markup = '''<div class="picCenter picCaption">
    <a href="%(fname)s" class="fresco" data-fresco-group="inline" data-fresco-group-options="ui: 'inside', thumbnails: 'vertical'" data-fresco-caption="%(title_text)s"><img class="lazy" data-original="%(fname)s" width="%(rel_width)d" height="%(rel_height)d" alt="%(alt_text)s" title="%(link_text)s" /><noscript><img src="%(fname)s" alt="%(alt_text)s" title="%(link_text)s"></img></noscript></a>
    <p><a href="%(fname)s" class="fresco" data-fresco-group="inline-text" data-fresco-group-options="ui: 'inside', thumbnails: 'vertical'" data-fresco-caption="%(title_text)s">%(title_text)s</a></p>
</div>'''
    elif mode=="thumb":
        print('<div class="gall">')
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
    dirList.sort()
    for fname in dirList:
        if re.search(r".jpg$", fname):
            sizes = getImageSizes(fname)
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
            print(template_markup % {"fname": fname, 'alt_text': alt_text, "link_text": link_text, "title_text": title_text, "rel_width": sizes["rel_width"], "rel_height": sizes["rel_height"]})
    if mode == "thumb":
        print('</div>')

if __name__ == '__main__':
    main()
