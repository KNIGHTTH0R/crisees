# OpenStreetMap Parser and Indexer
**Author: David Maxwell**
**Date: 2011-08-24**

This branch of Crisees has been developed to allow parsing of
OpenStreetMap OSM XML-formatted files, compressed down with Google
Protobuf. The Python package extracts all points of interest (POIs) from
within the supplied source file, as well as all the available streets.
These results can then be dealt with by however you like through use of
a custom made indexer module. By default, the Indexer module provided
stores them in a Whoosh index.

## How to Run the Parser
To run the parser, you must first install the required dependency - 
imposm - and its dependencies, too. Depending on how you want to store
the results, you may also need to install the Whoosh indexing package.

It's also briefly worth mentioning that this is a Python package, and as
such, Python is required to run this program. If you have not done
already, install the following package first.

* python

The imposm documentation - at http://imposm.org/docs/imposm/latest/ -
states the following dependencies are required before installation can
succeed:

* `psycopg2`
* Tokyo Cabinet
* Google Protobuf
* GEOS

Translated into package names, the following must be present and correct
for imposm to function on Ubuntu via aptitude:

* `build-essential`
* `python-dev`
* `protobuf-compiler`
* `libprotobuf-dev`
* `libtokyocabinet-dev`
* `python-psycopg2`
* `libgeos-c1`

For other distributions of Linux, the package names may vary/may not be
available by default through your favourite installation program. Having
run imposm successfully on Fedora core 14, the following packages should
be installed via yum:

* `python-devel`
* `protobuf-compiler`
* `tokyocabinet-devel`
* `python-psycopg2`
* `geos`
* `libprotobuf-dev`

Depending upon your setup, you may also need to install gcc, and it's
C++ counterpart. It's worth trying to install these packages to make
sure you have them; it won't do any damage if you already do.

* `gcc`
* `gcc-c++`

Once all the above have been successfully installed, you need to install
imposm. As it is listed in the Python Package Index, you can use pip or
easy_install to take care of the donkey work for you.

I'll use easy_install - just out of preference. Make sure it's available
by attempting to install the package

* `python-setuptools`

Once this package is installed, run the command

* `easy_install imposm`

You may get plenty of compiler warnings, but do not worry. As long as
you see a success message at the end of the output, you'll be okay. If
it fails for whatever reason, ensure all the packages listed above have
been successfully installed, and try again.

## Downloading a Source File
To do anything useful, you need a source protobuf file. This is
essentially an XML-based OpenStreetMap database dump. The major file,
planet.osm, contains EVERYTHING in the project - every POI and street on
the planet. As you can imagine, it is very large. You can find mirrors
to download it at http://wiki.openstreetmap.org/wiki/Planet.osm.

You may only be interested in a particular country, however. In which
case, you can download country-specific pbf files from Geofabrik, at URL
http://download.geofabrik.de/osm/. Ensure you download a .osm.pbf file
for your region of interest.

## Setting up an Indexer
You can write your own indexer, or make use of the one supplied - making
use of the excellent Whoosh indexing library. To use this, you need to
install Whoosh, by running the command

* `easy_install whoosh`

If you wish to write your own indexer, feel free to do so. For each POI/
street node, the parser provides five pieces of information, namely:

* The ID of the object
* The name of the object
* The object's latitude
* The object's longitude
* The type of the object (fire_station, railway_station etc.)

For each POI/street node, these are supplied in a dictionary with the
following keys:

* `item_id`
* `name`
* `latitude`
* `longitude`
* `place_type`

A custom indexer must extend the class Base, located in module
indexing.base. It must also be located in a subdirectory of the
indexing directory.

Let's have a look at an example. Say you wish to implement an sqlite
indexer.

Your directory structure would look thus:

```
    +
    |- osm_parser.py
    |
    |- indexing
    |  |
    |  | - __init__.py
    |  | - sqlite
    |  |   |
    |  |   | - __init__.py
    |  |   | - indexer.py
```

Note a subdirectory called "sqlite" in the "indexing" directory,
complete with an "indexer.py", where you place your custom code, and
"__init__.py" - telling the Python interpreter that the directory should
be treated as a Python module.

Within indexer.py, you must extend the indexing.base.Base class. A
sample file may look like:

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-

from indexing.base import Base

class Indexer(Base):
    def __init__(self, output):
        super(Indexer, self).__init__(output)
    
    def add(self, item):
        pass
        # Add item to your data store here
        # Item is a dictionary containing the five keys mentioned above.
    
    def stop(self):
        pass
        # Opportunity to commit any changes when stopping the program
```

Note that:

    * You must define a class called Indexer, extending Base.
    * The Indexer in its constructor must take a variable, output, which
      is passed to the base class. This variable contains the input from
      the command line, and provides the output location for your
      indexer. In the case of Whoosh, it represents an index directory,
      and in the case of Sqlite, it may represent your database output
      file.
    * Your Indexer class must provide an add method, with an item
      parameter. The item contains a dictionary with the five dictionary
      key/value pairs as mentioned previously.
    * A stop method must also be provided. This is only called when
      execution is interrupted or terminates normally. It gives you the
      option to include some code to commit any final changes to your
      data store.

To switch the indexer, open the file osm_parser.py. Change the global
variable INDEXER at the top of the file to match the name of your
indexer - in the case of the above example, it would become 'sqlite'.

## Running the Parser
Three arguments must be supplied to the main file, osm_parser.py, when
starting. They are:

* `--input=`
    Followed by the location of the downloaded .osm.pbf file.
* `--output=`
    Location of where output is stored.
* `--concurrency=`
    Allows for use of multiple cores/processors to speed up the time
    taken to complete the task. If on a unicore processor, use the
    value 1. Else, supply a value matching the number of
    cores/processors available to you. If your processor supports
    hyperthreading, double the value.

## Known Issues
The parser obtains a list of nodes that make up a way (a collection of
points which when joined up represent a street), and stores them in a
dictionary in memory. This can be quite memory-intensive if a large
input file is supplied. This could be rewritten to perhaps dump the
node references in a temporary sqlite database in the future.
