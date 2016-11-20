#!/usr/bin/env python
# encoding: utf-8
"""
otCMS.py

Classes and routines for otCMS

Created by Olivier Thereaux on 2013-01-03.
Copyright (c) 2013.
"""


__version_info__ = (0, 0, 1)
__version__ = '.'.join(map(str, __version_info__))
__author__ = "Olivier Thereaux"

import sys
import os
import unittest
import re
import markdown2
from os.path import join, dirname, exists
import ast


class otCMS:
    def __init__(self):
        pass


class otCMSTests(unittest.TestCase):
    def setUp(self):
        pass

class otCMSLocation(object):
    """Location (continent, country, etc) CMS"""
    uri = None
    name = None
    count = 0

    def __init__(self):
        super(otCMSLocation, self).__init__()


class otCMSEntry(object):
    """Entry (post, page) in the CMS"""
    uri = None
    title = None
    pubdate = None
    photos = None
    abstract = None
    thumbnail = None
    year = None
    continent = None
    country = None
    city = None
    region = None
    state = None
    location = None
    body = None
    language = None

    def __init__(self):
        super(otCMSEntry, self).__init__()

    def parameters():
        return ['uri', 'title', 'language','pubdate', 'pubdate_human', 'photos', 'abstract', 'year', 'continent', 'country', 'city', 'region', 'state', 'location', 'body']

    def __eq__(self, other):
        return self.uri == other.uri

    def fromdict(self, dict_entry):
        if "URI" in dict_entry:
            self.uri = dict_entry["URI"]
        if "Title" in dict_entry:
            self.title = dict_entry["Title"]
        if "Thumbnail" in dict_entry:
            self.thumbnail = dict_entry["Thumbnail"]
        if "Pubdate" in dict_entry:
            self.pubdate = dict_entry["Pubdate"]
            if self.pubdate != None:
                self.pubdate_human = re.sub(r"T.*", "", self.pubdate)
        if "Photos" in dict_entry:
            self.photos = dict_entry["Photos"]
        if "Abstract" in dict_entry:
            self.abstract = dict_entry["Abstract"]
        if "Language" in dict_entry:
            self.language = dict_entry["Language"]
        if "Year" in dict_entry:
            self.year = dict_entry["Year"]
        if "Continent" in dict_entry:
            self.continent = dict_entry["Continent"]
        if "Country" in dict_entry:
            self.country = dict_entry["Country"]
        if "City" in dict_entry:
            self.city = dict_entry["City"]
        if "Region" in dict_entry:
            self.region = dict_entry["Region"]
        if "State" in dict_entry:
            self.state = dict_entry["State"]
        if "Location" in dict_entry:
            self.location = dict_entry["Location"]
        if "Body" in dict_entry:
            self.body = dict_entry["Body"].decode("utf-8")

    def todict(self):
        dict_entry = dict()
        if self.uri != None:
            dict_entry["URI"] = self.uri
        if self.title != None:
            dict_entry["Title"] = self.title
        if self.thumbnail != None:
            dict_entry["Thumbnail"] = self.thumbnail
        if self.pubdate != None:
            dict_entry["Pubdate"] = self.pubdate
        if self.photos != None:
            dict_entry["Photos"] = self.photos
        if self.abstract != None:
            dict_entry["Abstract"] = self.abstract
        if self.year != None:
            dict_entry["Year"] = self.year
        if self.continent != None:
            dict_entry["Continent"] = self.continent
        if self.country != None:
            dict_entry["Country"] = self.country
        if self.city != None:
            dict_entry["City"] = self.city
        if self.region != None:
            dict_entry["Region"] = self.region
        if self.state != None:
            dict_entry["State"] = self.state
        if self.location != None:
            dict_entry["Location"] = self.location
        if self.body != None:
            dict_entry["Body"] = self.body
        if self.language != None:
            dict_entry["Language"] = self.language
        return dict_entry


    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __unicode__(self):
        # return u"%r" % self.__dict__
        return "%r" % self.todict()

    def __str__(self):
        return "%r" % self.todict()

class otCMSCatalog(list):
    def __init__(self):
        super(otCMSCatalog, self).__init__()

    def fromfile(self, catalog_path):
        entries=list()
        with open(catalog_path,"r") as catalog_fh:
            s = catalog_fh.read()
            entries = ast.literal_eval(s)
        for entry in entries:
            cms_entry = otCMSEntry()
            cms_entry.fromdict(entry)
            self.append(cms_entry)


if __name__ == '__main__':
    unittest.main()
