#!/usr/bin/env python
# encoding: utf-8
"""
refresh.py

Do-it-all script to refresh entries and indexes managed by otCMS
Created by Olivier Thereaux on 2013-01-03.
"""

import sys
import getopt
import os
import random
import re
import time
from os.path import join, dirname, exists, realpath
import markdown2

help_message = '''
refresh.py - regenerate entries and indexes
Options:
    -p      use the private catalog
    -h      this help message
'''


class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


def main(argv=None):
    private = False
    indexes = True
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hp", ["help", "noindex"])
        except getopt.error, msg:
            raise Usage(msg)
    
        # option processing
        for option, value in opts:
            if option == "-p":
                private = True
            if option == "--noindex":
                indexes = False
            if option in ("-h", "--help"):
                raise Usage(help_message)
    
    except Usage, err:
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
        print >> sys.stderr, "\t for help use --help"
        return 2

    # Setup template engine, path is known relative to the script
    from mako.template import Template
    from mako.lookup import TemplateLookup
    mylookup = TemplateLookup(directories=[join(dirname(__file__), "..", "templates")], output_encoding='utf-8', encoding_errors='replace')
    selection_template = mylookup.get_template("list_entry.html") # template for list of entries, used throughout

    # The library in ../lib/otCMS.py has some classes and helpers to manage entries
    source_tree_otCMS = join(dirname(__file__), "..", "lib", "otCMS.py")
    if exists(source_tree_otCMS):
        sys.path.insert(0, dirname(source_tree_otCMS))
        try:
            import otCMS
        finally:
            del sys.path[0]
    else:
        import otCMS
    
    # Parse the settings and load the entries catalog
    entries, path = otCMS.loadcatalog(private=private)  

    # This is where the web files should be found and written. 
    path = join(realpath(dirname(__file__)), path)
    if not exists(path):
        sys.exit(2)

    


    # 1.  Preparation for date-based archives / index
    years = list() # list of all years where there are entries
    yearly_selection = dict() # dict of entries per year
    yearly_all_html = u'' # html block with all entries, per year
    yearly_selection_html = dict() # dictionary of html block, per year
    yearly_lang_selection = dict()
    yearly_lang_selection['en'] = dict()
    yearly_lang_selection['fr'] = dict()
    yearly_lang_html = dict()
    yearly_lang_html['en'] = u''
    yearly_lang_html['fr'] = u''

    for entry in entries:
        if entry.year != None:
            if entry.year not in years:
                years.append(entry.year)
                yearly_selection[entry.year] = list()
                yearly_lang_selection['en'][entry.year] = list()
                yearly_lang_selection['fr'][entry.year] = list()
            yearly_selection[entry.year].append(entry)
            yearly_lang_selection[entry.language][entry.year].append(entry)
    for year in years:
        yearly_all_html = yearly_all_html + '''<h2 id="y%(year)s">%(year)s</h2>''' % {"year": year} 
        yearly_selection_html[year] = selection_template.render_unicode(selection = yearly_selection[year])
        yearly_all_html = yearly_all_html + selection_template.render_unicode(selection = yearly_selection[year])
        if yearly_lang_selection['en'].has_key(year):
            if len(yearly_lang_selection['en'][year]) > 0:
                yearly_lang_html['en'] = yearly_lang_html['en'] + '''<h2 id="y%(year)s">%(year)s</h2>''' % {"year": year} 
                yearly_lang_html['en'] = yearly_lang_html['en']+ selection_template.render_unicode(selection = yearly_lang_selection['en'][year])
        if yearly_lang_selection['fr'].has_key(year):
            if len(yearly_lang_selection['fr'][year]) > 0:
                yearly_lang_html['fr'] = yearly_lang_html['fr'] + '''<h2 id="y%(year)s">%(year)s</h2>''' % {"year": year} 
                yearly_lang_html['fr'] = yearly_lang_html['fr']+ selection_template.render_unicode(selection = yearly_lang_selection['fr'][year])
    
    # 2. Preparation for ocation based archives / index
    locations = list() # list of all locations. Should be alphabetically sorted
    location_types = dict() # dictionary of all locations per type (Continent, Country, etc)
    loc_selection = dict()  # dictionary of entries, per location
    loc_selection_html = dict() # HTML output
    
    for entry in entries:
        # this is a bit of a dance in order to make the catalog flexible.
        # it is possible for each catalog entry to have (or not have) values 
        # for Continent, Country, State, Region, City or Location
        # and each of these may either be a string or a list
        if entry.continent != None:
            continents = list()
            if type(entry.continent) != type(list()):
                continents.append(entry.continent)
            else: 
                continents = entry.continent
            for continent in continents:
                if continent not in locations:
                    locations.append(continent)
                    location_types[continent] = "Continent"
                    loc_selection[continent] = list()
                loc_selection[continent].append(entry)
        if entry.country != None:
            countries = list()
            if type(entry.country) != type(list()):
                countries.append(entry.country)
            else:
                countries = entry.country
            for country in countries:
                if country not in locations:
                    locations.append(country)
                    location_types[country] = "Country"
                    loc_selection[country] = list()
                loc_selection[country].append(entry)  
        if entry.city != None:
            cities = list()
            if type(entry.city) != type(list()):
                cities.append(entry.city)
            else:
                cities = entry.city
            for city in cities:
                if city not in locations:
                    locations.append(city)
                    location_types[city] = "City"
                    loc_selection[city] = list()
                loc_selection[city].append(entry)
        if entry.state != None:
            states = list()
            if type(entry.state) != type(list()):
                states.append(entry.state)
            else:
                states = entry.state
            for state in states:        
                if state not in locations:
                    locations.append(state)
                    location_types[state] = "State"
                    loc_selection[state] = list()
                loc_selection[state].append(entry)
        if entry.region != None:
            regions = list()
            if type(entry.region) != type(list()):
                regions.append(entry.region)
            else:
                regions = entry.region
            for region in regions:            
                if region not in locations:
                    locations.append(region)
                    location_types[region] = "Region"
                    loc_selection[region] = list()
                loc_selection[region].append(entry)
        if entry.location != None:
            locs = list()
            if type(entry.location) != type(list()):
                locs.append(entry.location)
            else:
                locs = entry.location
            for loc in locs:            
                if loc not in locations:
                    locations.append(loc)
                    location_types[loc] = "Location"
                    loc_selection[loc] = list()
                loc_selection[loc].append(entry)
    locations.sort()

    # 3. Generate individual entries from their MarkDown source
    for entry in entries:
        source = entry.uri
        source = re.sub(r"^/", "", source)
        if re.search(r".*\.html$", source):
            dest = source
            source = re.sub(r"\.html$", ".md", source)
        elif re.search(r".*/$", source):
            dest = re.sub(r"$", "index.html", source)
            source = re.sub(r"$", "index.md", source)
        else:
            dest = source+".html"
            source = source+".md"
        source_fn = join(path, source)
        page_html = markdown2.markdown_path(source_fn)
        entry.body = page_html
        dest_fn = join(path, dest)
        dest_fh = open(dest_fn, "w")
        mytemplate = mylookup.get_template("page.html")
        dest_fh.write( mytemplate.render_unicode(
                                        body= page_html,
                                        title= entry.title,  
                                        page_type="Page",
                                        page_description = entry.abstract,
                                        page_language = entry.language
                                        ).encode("utf-8") )
        dest_fh.close()
        if re.search(r"index", source):
            rdf = re.sub(r"index\..*", "", source)+"meta.rdf"
            rdf_fn = join(path, rdf)
            rdf_fh = open(rdf_fn, "w")
            mytemplate = mylookup.get_template("meta.rdf")
            rdf_fh.write( mytemplate.render_unicode(
                                            uri= entry.uri,
                                            title= entry.title).encode("utf-8") )
            rdf_fh.close()


    # 4. Generate archives pages

    if private == False and indexes == True: # do not generate archives and indexes for private entries

        # 4.1 Generate full archive
        mytemplate = mylookup.get_template("index_all.html")
        index = open(join(path, 'all.html.tmp'), 'w')
        index.write( mytemplate.render_unicode(
                                        yearly_entries=yearly_all_html,
                                        title='Archives',  
                                        page_type="Index",
                                        page_description = "",
                                        page_intro = u'',
                                        page_language = ""
                                        ).encode("utf-8") )
        os.rename(join(path, 'all.html.tmp'), join(path, 'all.html'))



        # 4.1 Generate lang-based archive
        for lang in ['en', 'fr']:
            if lang == 'en':
                title= u"Archives: in English"
            else: #fr
                title= u"Archives: en Français"
            
            filename = "all_"+lang+'.html'
            filename_tmp = "all_"+lang+'.html.tmp'
            desc_template = mylookup.get_template("intro_"+lang+".html")
            desc_template.render_unicode()
            mytemplate = mylookup.get_template("index_all.html")
            index = open(join(path, filename_tmp), 'w')
            index.write( mytemplate.render_unicode(
                                            yearly_entries=yearly_lang_html[lang],
                                            title= title,  
                                            page_type="Index",
                                            page_description = '',
                                            page_intro = desc_template.render_unicode(),
                                            page_language = lang
                                            ).encode("utf-8") )
            os.rename(join(path, filename_tmp), join(path, filename))


        # 4.2 Generate per-year archive pages 
        for year in years:
            mytemplate = mylookup.get_template("index_generic.html")
            index = open(join(path, str(year), 'index.html.tmp'), 'w')
            index.write( mytemplate.render_unicode(
                                            entries=yearly_selection_html[year],
                                            title='Archives: ' + str(year) ,  
                                            page_type="Index",
                                            intro = '',
                                            page_description = "",
                                            page_language = ""
                                            ).encode("utf-8") )
            os.rename(join(path, str(year), 'index.html.tmp'), join(path, str(year), 'index.html'))

        # 4.3 Generate main /geo index
        geo_html = u''
        reverse_loc_bytype = dict()
        geo_index_template = mylookup.get_template("index_generic.html")
        geo_block_template = mylookup.get_template("list_location.html")

        for loctype in ['Continent', 'Country', 'Region', 'State', 'City', 'Location']:
            reverse_loc_bytype[loctype] = list()

        for loc_name in locations:
            loc_obj = otCMS.otCMSLocation()
            loc_obj.uri = "/geo/"+re.sub (" ", "_", loc_name.lower())
            loc_obj.uri = re.sub (",", "", loc_obj.uri)
            loc_obj.name = loc_name
            loc_obj.count = len(loc_selection[loc_name])
            reverse_loc_bytype[location_types[loc_name]].append(loc_obj)
        for loctype in ['Continent', 'Country', 'Region', 'State', 'City', 'Location']:
            geo_html = geo_html + geo_block_template.render_unicode(
                                            loctype= loctype, locations = reverse_loc_bytype[loctype]
                                            ).encode("utf-8")
                                    
        index = open(join(path, "geo", 'index.html.tmp'), 'w')
        index.write( geo_index_template.render_unicode(
                                        entries= '',
                                        title=u'Archives: Around the world',  
                                        page_type="Index",
                                        intro = geo_html,
                                        page_description = "",
                                        page_language = ""
                                        ).encode("utf-8") )
        os.rename(join(path, "geo", 'index.html.tmp'), join(path, "geo", 'index.html'))
    
        # 4.4 Generate individual geo pages
        for loc_name in locations:
            loc = re.sub (" ", "_", loc_name.lower())
            loc = re.sub (",", "", loc)
            loc_selection_html[loc] = selection_template.render_unicode(selection = loc_selection[loc_name])
            mytemplate = mylookup.get_template("index_generic.html")
            index = open(join(path, "geo", loc+'.html.tmp'), 'w')
            index.write( mytemplate.render_unicode(
                                            entries= loc_selection_html[loc],
                                            title=u'Entries in ' + location_types[loc_name] +": "+ loc_name,  
                                            page_type="Index",
                                            intro = '',
                                            page_description = "",
                                            page_language = ""
                                            ).encode("utf-8") )
            os.rename(join(path, "geo", loc+'.html.tmp'), join(path, "geo", loc+'.html'))


        # 5. Generate the Home Page 

        latest_selection=entries[0:4]
        entries_featurable = list()
        for entry in entries:
            if entry.abstract != None and entry.thumbnail != None and entry not in latest_selection:
                entries_featurable.append(entry)
        random_selection=random.sample(entries_featurable, 4)
        latest_selection_html = selection_template.render_unicode(selection = latest_selection)
        random_selection_html = selection_template.render_unicode(selection = random_selection)
        title= u"2 Neurones &amp; 1 Camera - by @olivierthereaux"
        page_description = u'Travelogue, street photography, a bit of poetry, and the simple pleasure of telling stories. Around the world, from Europe to Japan, from Paris to London via Tokyo and Montreal'
        page_type = "Home"
        mytemplate = mylookup.get_template("index_main.html")
        index = open(join(path, 'index.html.tmp'), 'w')


        index.write( mytemplate.render_unicode(
                                        latest_selection=latest_selection_html, 
                                        random_selection=random_selection_html, 
                                        title=title, page_description=page_description, 
                                        page_type=page_type,
                                        page_language = ""
                                        ).encode("utf-8") )

        index.close()
        os.rename(join(path, 'index.html.tmp'), join(path, 'index.html'))

        # 5. Generate the Atom Feed 

        atom_selection=entries[0:20]
        mytemplate = mylookup.get_template("atom.xml")
        index = open(join(path, 'atom.xml.tmp'), 'w')
        latest_pubdate = atom_selection[0].pubdate
        
        index.write( mytemplate.render_unicode(
                                        atom_selection=atom_selection, 
                                        latest_pubdate=latest_pubdate
                                        ).encode("utf-8") )
        index.close()
        os.rename(join(path, 'atom.xml.tmp'), join(path, 'atom.xml'))
        
if __name__ == "__main__":
    sys.exit(main())



