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
    
    def __init__(self):
        super(otCMSEntry, self).__init__()

    def parameters():
        return ['uri', 'title', 'pubdate', 'pubdate_human', 'photos', 'abstract', 'year', 'continent', 'country', 'city', 'region', 'state', 'location', 'body']
    
    def fromdict(self, dict_entry):
        if dict_entry.has_key("URI"):
            self.uri = dict_entry["URI"]
        if dict_entry.has_key("Title"):
            self.title = dict_entry["Title"]
        if dict_entry.has_key("Thumbnail"):
            self.thumbnail = dict_entry["Thumbnail"]
        if dict_entry.has_key("Pubdate"):
            self.pubdate = dict_entry["Pubdate"]
            if self.pubdate != None:
                self.pubdate_human = re.sub(r"T.*", "", self.pubdate)
        if dict_entry.has_key("Photos"):
            self.photos = dict_entry["Photos"]
        if dict_entry.has_key("Abstract"):
            self.abstract = dict_entry["Abstract"]
        if dict_entry.has_key("Year"):
            self.year = dict_entry["Year"]
        if dict_entry.has_key("Continent"):
            self.continent = dict_entry["Continent"]
        if dict_entry.has_key("Country"):
            self.country = dict_entry["Country"]
        if dict_entry.has_key("City"):
            self.city = dict_entry["City"]
        if dict_entry.has_key("Region"):
            self.region = dict_entry["Region"]
        if dict_entry.has_key("State"):
            self.state = dict_entry["State"]
        if dict_entry.has_key("Location"):
            self.location = dict_entry["Location"]
        if dict_entry.has_key("Body"):
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
        return dict_entry


    def __repr__(self):
        return "%s(%r)" % (self.__class__, self.__dict__)

    def __unicode__(self):
        # return u"%r" % self.__dict__
        return u"%r" % self.todict()

    def __str__(self):
        return "%r" % self.todict()

def loadcatalog(private):
    entries = list()
    path = "./"
    settings = join(dirname(__file__), "..", "config", "settings.py")
    exec(open(settings,"rb").read())
    catalog = ''
    if private == True:
        catalog = join(dirname(__file__), private_catalog)
    else:
        catalog = join(dirname(__file__), public_catalog)
    exec(open(catalog,"rb").read())
    converted_entries = list()
    for entry in entries:
        cms_entry = otCMSEntry()
        cms_entry.fromdict(entry)
        converted_entries.append(cms_entry)
    return converted_entries, path
        

if __name__ == '__main__':
	unittest.main()