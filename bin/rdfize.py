#!/usr/bin/env python
# encoding: utf-8
"""
rdfize.py

Generate photordf for all images in current directory

Created by olivier Thereaux on 2008-12-21.
"""

import sys
import os
import re

def main():
    rdf_template = u"""<?xml version='1.0' encoding='utf-8'?>
      <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
          xmlns:rdfs="http://www.w3.org/TR/1999/PR-rdf-schema-19990303#"
          xmlns:s0="http://www.w3.org/2000/PhotoRDF/dc-1-0#"
          xmlns:s1="http://sophia.inria.fr/~enerbonn/rdfpiclang#">
        <rdf:Description rdf:about="">
          <s1:xmllang>fr</s1:xmllang>
          <s0:type>image</s0:type>
          <s0:format>image/jpeg</s0:format>
          <s0:creator>Olivier Thereaux</s0:creator>
          <s0:title>%(TITLE)s</s0:title>
          <s0:coverage>%(LOCATION)s</s0:coverage>
          <s0:description>%(DESCRIPTION)s%(DELIMITER)s%(LOCATION)s</s0:description>
          <s0:date>%(DATE)s</s0:date>
        </rdf:Description>
      </rdf:RDF>
    """
    album_location = raw_input('Location?    ')
    album_date = raw_input('Date?    ')
    dirList=os.listdir(".")
    for fname_img in dirList:
        if re.search(r".jpg$", fname_img):
            fname_rdf = re.sub(".jpg", ".rdf", fname_img)
            print(u"\nProcessing %s…" % fname_img)
            infer_title = fname_img
            infer_title = re.sub("_", " ", infer_title)
            infer_title = re.sub("\d+-", "", infer_title)
            infer_title = re.sub(".jpg", "", infer_title)
            infer_title = re.sub(r"[0-9-]+$", "", infer_title)
            input_title = raw_input('Title? (Default: %s)    ' % infer_title)
            if input_title == "":
                input_title = infer_title
            input_location = raw_input('Location? (Default: %s)    ' % album_location)
            if input_location == "":
                input_location = album_location
            input_date = raw_input('Date? (Default: %s)    ' % album_date)
            if input_date == "":
                input_date = album_date
            input_desc = raw_input('Description? (Default: %s) ' % input_title)
            delimiter = u" "
            if input_desc == "":
                input_desc = input_title
            if (len(input_desc) != 0):
                if (input_desc[-1] != u"."):
                    delimiter = u" - "
                    
            rdf_text = rdf_template % {"TITLE": input_title.decode("utf-8"), "LOCATION": input_location.decode("utf-8"), 
            "DATE": input_date.decode("utf-8"), "DESCRIPTION": input_desc.decode("utf-8"), "DELIMITER": delimiter}
            file_rdf = open(fname_rdf, 'w')
            file_rdf.write(rdf_text.encode("utf-8"))
            file_rdf.close()

if __name__ == "__main__":
    sys.exit(main())
