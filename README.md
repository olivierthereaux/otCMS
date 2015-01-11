# otCMS

otCMS is the diminutive CMS used to run the site [olivier.thereaux.net](http://olivier.thereaux.net/). 

## Ceci n'est pas un CMS

* *No dynamic code*. My site doen't have comments, accounts, personalisation or any such thing. It means I can write or generate flat HTML files, and the site will “just work” pretty much wherever I serve it from - even if the CMS is broken.
* *Minimal dependencies*. This CMS is written in python, which comes by default with a very rich library. I did not want to depend on too many libraries which would hinder portability. So far, I have managed to stick to two library dependencies, and imagemagick for thumbnail creation 
* *No database* - The catalog of entries is a flat file, both machine-readable and human-writable. I looked at a few formats (such as yaml) but decided to stick to a python syntax. See samples/catalog.py.
* *Simple publication mechanism*. A few scripts should be enough to (re)generate html files with simple templates. Git or any other versioning system can then take over as versioning, distribution and backup mechanism.
* *No editor*. I write entries by hand, using a mix of markdown and HTML. The CMS takes care of adding all the navigation, headers, footers and generates all the indexes and feeds. 

## Dependencies

You will need

* Python, with the
    * [python-markdown2](https://github.com/trentm/python-markdown2) and 
    * [mako](http://www.makotemplates.org/) modules
* Imagemagick for the thumbnail generation

## HOWTO

* Connect with your htdocs directory by setting the right parameters in config/settings.py
* Create your catalog of entries. See samples/catalog.py
* [optional] You can write entries by editing a .md file. The system will take that as a basis to create .html entries
* Run bin/refresh.py to create/refresh indexes, feeds, and entries

## TODO

* Pre-processing for a few usual markup constructs (image gallery, etc)

## Authors / Copying

(c) 2013-2015 Olivier Thereaux (olivier@thereaux.net)

This work is free. You can redistribute it and/or modify it under the
terms of the Do What The Fuck You Want To Public License, Version 2,
as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

