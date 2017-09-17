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
import cgi
import time
from os.path import join, dirname, exists, realpath
import markdown2
from feedgen.feed import FeedGenerator

# The library in ../lib/otCMS.py has some classes and helpers to manage entries
source_tree_otCMS = realpath(join(dirname(__file__), "..", "lib", "otCMS.py"))
if exists(source_tree_otCMS):
    sys.path.insert(0, dirname(source_tree_otCMS))
    try:
        import otCMS
    finally:
        del sys.path[0]
else:
    import otCMS



def usage():
    print('''
refresh.py - regenerate entries and indexes

Usage: refresh.py [Options]

Optional

Options:
    --catalog   set path for entries catalog.
                By default, will look for "catalog.py" in current directory
      ... or "private.py" if option "-p" is set (see below)
    --htdocs    set path for where the entries should be generated
                By default, will consider path of catalog file to be the root
    -p          use  private catalog.
                Will only generate entries, no indexes
    -h (--help) This help message
''')
    sys.exit(2)



def main(argv=None):
    private = False
    catalog_path =  realpath(os.path.curdir) # by default
    htdocs = None
    catalog = None
    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hp", ["help", "catalog=", "htdocs="])
        except getopt.error as msg:
            usage()

        # option processing
        for option, value in opts:
            if option == "-p":
                private = True
            if option == "--noindex":
                indexes = False
            if option in ("-h", "--help"):
                usage()
            if option == "--catalog":
                catalog = value
            if option == "--htdocs":
                htdocs = realpath(value)

    except Exception as e:
        print(e)
        usage()



    # Try loading catalog
    if catalog: # specified by user
        catalog = join(catalog_path, catalog)
        if not os.path.isfile(catalog):
            help_message = "could not find catalog file %s" % catalog
            usage()

    else: #not specified by user
        try:
            catalog_path = realpath(os.path.curdir)
            while catalog_path != "/" and not catalog:
                if private:
                    catalog = join(catalog_path, "private.py")
                else:
                    catalog = join(catalog_path, "catalog.py")
                # print("Trying to open default catalog file %s" % catalog)
                if os.path.isfile(catalog):
                    print("Found default catalog file %s" % catalog)
                else:
                    catalog = None
                    catalog_path = realpath(join(catalog_path, ".."))
            if not os.path.isfile(catalog):
                print("Error: could not find defaut catalog file %s" % catalog)
                usage()
        except Exception as e:
            print(e)
            usage()

    try:
        entries = otCMS.otCMSCatalog()
        entries.fromfile(catalog)
        print("Catalog read successfully. %d entries loaded" % len(entries))
    except Exception as e:
        print(e)
        usage()

    if htdocs: #specified by user
        if os.path.exists(htdocs):
            pass
        else:
            print("Error: could not find root path for htdocs: %s" % htdocs)
            usage()
    else:
        htdocs=catalog_path
    print("Writing files with %s as htdocs root directory" % htdocs)

    # Setup template engine, path is known relative to the script
    from mako.template import Template
    from mako.lookup import TemplateLookup
    mylookup = TemplateLookup(directories=[join(dirname(__file__), "..", "templates")], output_encoding='utf-8', encoding_errors='replace')
    selection_template = mylookup.get_template("list_entry.html") # template for list of entries, used throughout


    # 1.  Preparation for date-based archives / index
    years = list() # list of all years where there are entries
    yearly_selection = dict() # dict of entries per year
    yearly_all_html = '' # html block with all entries, per year
    yearly_selection_html = dict() # dictionary of html block, per year
    yearly_lang_selection = dict()
    yearly_lang_selection['en'] = dict()
    yearly_lang_selection['fr'] = dict()
    yearly_lang_html = dict()
    yearly_lang_html['en'] = ''
    yearly_lang_html['fr'] = ''

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
        if year in yearly_lang_selection['en']:
            if len(yearly_lang_selection['en'][year]) > 0:
                yearly_lang_html['en'] = yearly_lang_html['en'] + '''<h2 id="y%(year)s">%(year)s</h2>''' % {"year": year}
                yearly_lang_html['en'] = yearly_lang_html['en']+ selection_template.render_unicode(selection = yearly_lang_selection['en'][year])
        if year in yearly_lang_selection['fr']:
            if len(yearly_lang_selection['fr'][year]) > 0:
                yearly_lang_html['fr'] = yearly_lang_html['fr'] + '''<h2 id="y%(year)s">%(year)s</h2>''' % {"year": year}
                yearly_lang_html['fr'] = yearly_lang_html['fr']+ selection_template.render_unicode(selection = yearly_lang_selection['fr'][year])

    # 2. Preparation for location based archives / index
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
        i=entries.index(entry)
        previous = entries[i-1] if i>0 else None
        # ignoring non-dated entry pages
        if previous:
            if previous.year == None:
                previous = None
        next = entries[i+1] if i<len(entries)-1 else None
        # ignoring non-dated entry pages
        if next:
            if next.year == None:
                next = None

        previous_html_block = selection_template.render_unicode(selection = [previous]) if previous else ''
        next_html_block = selection_template.render_unicode(selection = [next]) if next else ''
        mytemplate = mylookup.get_template("prevnext.html")
        if entry.year == None: # for contact page etc, non-dated stuff; no need for that nav
            prevnext_html = ''
        else:
            prevnext_html = mytemplate.render_unicode(
                                        previous_body= previous_html_block,
                                        next_body= next_html_block,
                                        page_language = entry.language
                                        )

        mytemplate = mylookup.get_template("nearby.html")
        nearby_list = list()
        if entry.city != None:
            try:
                nearby_list= nearby_list+loc_selection[entry.city]
                nearby_list = sorted(set(nearby_list))
                nearby_list.remove(entry)
            except:
                pass
        if entry.state != None and len(nearby_list) < 5:
            try:
                nearby_list= nearby_list+loc_selection[entry.state]
                nearby_list = sorted(set(nearby_list))
                nearby_list.remove(entry)
            except:
                pass
        if entry.region != None and len(nearby_list) < 5:
            try:
                nearby_list= nearby_list+loc_selection[entry.region]
                nearby_list = sorted(set(nearby_list))
                nearby_list.remove(entry)
            except:
                pass
        if entry.country != None and len(nearby_list) < 5:
            try:
                nearby_list= nearby_list+loc_selection[entry.country]
                nearby_list = sorted(set(nearby_list))
                nearby_list.remove(entry)
            except:
                pass
        # After a bit of experimentation, going beyond Country feels to broad
        # if entry.continent != None and len(nearby_list) < 3:
        #     try:
        #         nearby_list= nearby_list+loc_selection[entry.continent]
        #         nearby_list = sorted(set(nearby_list))
        #         nearby_list.remove(entry)
        #     except:
        #         pass
        if len(nearby_list)> 0:
            nearby_list_dedup = list()
            nearby_list_dedup_index = list()
            for nearby_entry in nearby_list:
                if nearby_entry.uri == entry.uri:
                    pass
                elif nearby_entry.uri in nearby_list_dedup_index:
                    pass
                else:
                    nearby_list_dedup_index.append(nearby_entry.uri)
                    nearby_list_dedup.append(nearby_entry)
            nearby_list = nearby_list_dedup
        if len(nearby_list)>5:
            nearby_list=random.sample(nearby_list, 5)

        nearby_html_block = selection_template.render_unicode(selection = nearby_list) if len(nearby_list)>0 else ''
        nearby_html = ''
        if nearby_list:
            nearby_html = mytemplate.render_unicode(
                                            nearby_body = nearby_html_block,
                                            page_language = entry.language
                                            )


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
        source_fn = join(htdocs, source)
        page_html = markdown2.markdown_path(source_fn)
        page_html = page_html.replace("<p></div></p>", "</div>") # workaround for annoying markdown behavior
        entry.body = page_html
        dest_fn = join(htdocs, dest)
        dest_fh = open(dest_fn, "w")
        mytemplate = mylookup.get_template("page.html")
        tag_re = re.compile(r'(<!--.*?-->|<[^>]*>)')
        clean_abstract = ''
        if entry.abstract:
            clean_abstract = tag_re.sub('', entry.abstract)
            clean_abstract = re.sub('[<>]', '', clean_abstract)
        dest_fh.write( mytemplate.render_unicode(
                                        body= page_html,
                                        title= entry.title,
                                        page_type="Page",
                                        page_description = clean_abstract,
                                        page_language = entry.language,
                                        prevnext_body = prevnext_html,
                                        nearby_body = nearby_html
                                        ))
        dest_fh.close()

        if re.search(r"index", source):
            rdf = re.sub(r"index\..*", "", source)+"meta.rdf"
            rdf_fn = join(htdocs, rdf)
            rdf_fh = open(rdf_fn, "w")
            mytemplate = mylookup.get_template("meta.rdf")
            rdf_fh.write( mytemplate.render_unicode(
                                            uri= entry.uri,
                                            title= entry.title) )
            rdf_fh.close()


    # 4. Generate archives pages

    if private == False: # do not generate archives and indexes for private entries

        # 4.1 Generate full archive
        mytemplate = mylookup.get_template("index_all.html")
        index = open(join(htdocs, 'all.html.tmp'), 'w')
        index.write( mytemplate.render_unicode(
                                        yearly_entries=yearly_all_html,
                                        title='Archives',
                                        page_type="Index",
                                        page_description = "",
                                        page_intro = '',
                                        page_language = "",
                                        page_include_nav = 1
                                        ))
        os.rename(join(htdocs, 'all.html.tmp'), join(htdocs, 'all.html'))



        # 4.1 Generate lang-based archive
        for lang in ['en', 'fr']:
            if lang == 'en':
                title= "Archives: in English"
            else: #fr
                title= "Archives: en Français"

            filename = "all_"+lang+'.html'
            filename_tmp = "all_"+lang+'.html.tmp'
            desc_template = mylookup.get_template("intro_"+lang+".html")
            desc_template.render_unicode()
            mytemplate = mylookup.get_template("index_all.html")
            index = open(join(htdocs, filename_tmp), 'w')
            index.write( mytemplate.render_unicode(
                                            yearly_entries=yearly_lang_html[lang],
                                            title= title,
                                            page_type="Index",
                                            page_description = '',
                                            page_intro = desc_template.render_unicode(),
                                            page_language = lang,
                                            page_include_nav = None
                                            ) )
            os.rename(join(htdocs, filename_tmp), join(htdocs, filename))


        # 4.2 Generate per-year archive pages
        for year in years:
            mytemplate = mylookup.get_template("index_generic.html")
            index = open(join(htdocs, str(year), 'index.html.tmp'), 'w')
            index.write( mytemplate.render_unicode(
                                            entries=yearly_selection_html[year],
                                            title='Archives: ' + str(year) ,
                                            page_type="Index",
                                            intro = '',
                                            page_description = "",
                                            page_language = ""
                                            ) )
            os.rename(join(htdocs, str(year), 'index.html.tmp'), join(htdocs, str(year), 'index.html'))

        # 4.3 Generate main /geo index
        geo_html = ''
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
                                            )

        index = open(join(htdocs, "geo", 'index.html.tmp'), 'w')
        index.write( geo_index_template.render_unicode(
                                        entries= '',
                                        title='Archives: Around the world',
                                        page_type="Index",
                                        intro = geo_html,
                                        page_description = "",
                                        page_language = ""
                                        ) )
        os.rename(join(htdocs, "geo", 'index.html.tmp'), join(htdocs, "geo", 'index.html'))

        # 4.4 Generate individual geo pages
        for loc_name in locations:
            loc = re.sub (" ", "_", loc_name.lower())
            loc = re.sub (",", "", loc)
            loc_selection_html[loc] = selection_template.render_unicode(selection = loc_selection[loc_name])
            mytemplate = mylookup.get_template("index_generic.html")
            index = open(join(htdocs, "geo", loc+'.html.tmp'), 'w')
            index.write( mytemplate.render_unicode(
                                            entries= loc_selection_html[loc],
                                            title='Entries in ' + location_types[loc_name] +": "+ loc_name,
                                            page_type="Index",
                                            intro = '',
                                            page_description = "",
                                            page_language = ""
                                            ) )
            os.rename(join(htdocs, "geo", loc+'.html.tmp'), join(htdocs, "geo", loc+'.html'))


        # 5. Generate the Home Page

        latest_selection=entries[0:4]
        entries_featurable = list()
        for entry in entries:
            if entry.abstract != None and entry.thumbnail != None and entry not in latest_selection:
                entries_featurable.append(entry)
        random_selection=random.sample(entries_featurable, 4)
        latest_selection_html = selection_template.render_unicode(selection = latest_selection)
        random_selection_html = selection_template.render_unicode(selection = random_selection)
        title= "2 Neurones &amp; 1 Camera - by @olivierthereaux"
        page_description = 'Travelogue, street photography, a bit of poetry, and the simple pleasure of telling stories. Around the world, from Europe to Japan, from Paris to London via Tokyo and Montreal'
        page_type = "Home"
        mytemplate = mylookup.get_template("index_main.html")
        index = open(join(htdocs, 'index.html.tmp'), 'w')


        index.write( mytemplate.render_unicode(
                                        latest_selection=latest_selection_html,
                                        random_selection=random_selection_html,
                                        title=title, page_description=page_description,
                                        page_type=page_type,
                                        page_language = ""
                                        ) )

        index.close()
        os.rename(join(htdocs, 'index.html.tmp'), join(htdocs, 'index.html'))

        # 5. Generate the Atom Feed

        atom_selection=entries[0:20]
        fg = FeedGenerator()
        fg.id('tag:olivier.thereaux.net,2000:1337')
        fg.title('2 Neurones and 1 Camera')
        # fg.author( {'name':'Olivier Thereaux','uri':'https://olivier.thereaux.net/contact'} )
        fg.author( {'name':'Olivier Thereaux'} )
        fg.link( href='https://olivier.thereaux.net/', rel='alternate' )
        fg.subtitle('Olivier Thereaux')
        fg.link( href='https://olivier.thereaux.net/atom.xml', rel='self' )

        for entry in atom_selection:
            fe = fg.add_entry()
            fe.updated(entry.pubdate)
            entry_id = "https://olivier.thereaux.net"+entry.uri
            fe.published(entry.pubdate)
            fe.id(entry_id)
            fe.author( {'name':'Olivier Thereaux'} )
            entry_link = {"rel": "alternate", "type":"text/html", "href": "https://olivier.thereaux.net"+entry.uri}
            fe.link(entry_link)
            fe.title(entry.title)

            if entry.abstract:
                fe.summary(entry.abstract)
            if entry.abstract:
                entry_content = '<p>%s</p>' % entry.abstract
                if entry.language == "fr":
                    if entry.photos != None:
                        entry_content =entry_content +'<p><a href="%s">À suivre / %s photos</a></p>' % (entry_id, entry.photos)
                    else:
                        entry_content =entry_content +'<p><a href="%s">À suivre</a></p>' % entry_id
                else:
                    if entry.photos != None:
                        entry_content =entry_content +'<p><a href="%s">À suivre / %s photos</a></p>' % (entry_id, entry.photos)
                    else:
                        entry_content =entry_content +'<p><a href="%s">À suivre</a></p>' % entry_id
                if entry.thumbnail:
                    entry_thumbnail_big = entry.thumbnail
                    entry_thumbnail_big = re.sub("tn/tn_", "tn/lg_", entry.thumbnail)
                    entry_content =entry_content +'<img src="https://olivier.thereaux.net%s" width="500px" height="500px" />' % entry_thumbnail_big
                fe.content(entry_content, type="html")

            entry.body_abs = entry.body

            entry.body = re.sub(r'src="([0-9])', 'src="'+entry_id+'tn/lg_\\1', entry.body, count=0)
            # entry.body = re.sub(r'src="([0-9])', 'src="'+entry_id+'\\1', entry.body, count=0)
            entry.body = re.sub(r'src="tn', 'src="'+entry_id+"tn", entry.body, count=0)
            entry.body = re.compile(r'<a href[^>]*>(.*)</a>', re.MULTILINE).sub('\\1', entry.body, count=0)
            entry.body = re.sub(r'<img class="lazy".* />', '', entry.body, count=0)
            entry.body = re.sub(r'<img src', '<img width="600" src', entry.body, count=0)
            entry.body = re.sub(r'<noscript>(.*)</noscript>', '\\1', entry.body, count=0)
            entry.body = re.compile('<div class="picCenter picCaption">\s*<img(.*)/img>\s*<p>(.*)</p>\s*</div>', re.MULTILINE).sub("<img\\1/img><p><i>\\2</i></p>",entry.body, count=0)
            entry.body = re.compile('<div class="picCenter picCaption">\s*<img(.*) />\s*<p>(.*)</p>\s*</div>', re.MULTILINE).sub("<img\\1 /><p><i>\\2</i></p>",entry.body, count=0)
            fe.content(entry.body,type="CDATA")
        atom_xml = fg.atom_str(pretty=True).decode("utf-8")
        # Nasty Hack to add a type=html property to the summary element ...
        atom_fh = open(join(htdocs, 'atom.xml.tmp'), "w") # Write the ATOM feed to a file
        atom_fh.write(atom_xml)
        atom_fh.close()
        os.rename(join(htdocs, 'atom.xml.tmp'), join(htdocs, 'atom.xml'))

        # rss_xml = fg.rss_str(pretty=True).decode("utf-8")
        # # Nasty Hack to add a type=html property to the summary element ...
        # rss_fh = open(join(htdocs, 'rss.xml.tmp'), "w") # Write the ATOM feed to a file
        # rss_fh.write(rss_xml)
        # rss_fh.close()
        # os.rename(join(htdocs, 'rss.xml.tmp'), join(htdocs, 'rss.xml'))


        # mytemplate = mylookup.get_template("atom.xml")
        # index = open(join(htdocs, 'atom.xml.tmp'), 'w')
        # latest_pubdate = atom_selection[0].pubdate
        #
        # index.write( mytemplate.render_unicode(
        #                                 atom_selection=atom_selection,
        #                                 latest_pubdate=latest_pubdate
        #                                 ) )
        # index.close()
        # os.rename(join(htdocs, 'atom.xml.tmp'), join(htdocs, 'atom.xml'))

if __name__ == "__main__":
    sys.exit(main())
