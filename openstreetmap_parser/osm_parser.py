#!/usr/bin/env python
# -*- coding: utf-8 -*-

from callbacks.coordinates import Coordinates
from callbacks.nodes import Nodes
from callbacks.ways import Ways
from sys import argv
import os

# Specify the indexer you wish to use here.
# Leave the other three variables as they are!

INDEXER     = 'whoosh'

INPUT       = ''
OUTPUT      = ''
CONCURRENCY = 1

def checks(argv):
	try:
		__import__('imposm.parser')
	except ImportError:
		print "The imposm parser could not be imported.\n" \
			  "Please check the imposm package is correctly installed, and try again."
		quit()
	
	try:
		__import__('indexing.%s.indexer' % INDEXER)
	except ImportError:
		print "The selected indexer could not be found."
	
	if len(argv) == 0:
		print "Usage: osm_parser.py --input=INPUT.osm.pbf --output=OUTPUT_NAME --concurrency=x"
		quit()
	else:
		found_input = False
		found_output = False
		found_concurrency = False
		
		for string in argv:
			if string.startswith('--input='):
				global INPUT
				INPUT = string[8:]
				found_input = True
			if string.startswith('--output='):
				global OUTPUT
				OUTPUT = string[9:]
				found_output = True
			if string.startswith('--concurrency='):
				global CONCURRENCY
				CONCURRENCY = int(string[14:])
				found_concurrency = True
		
		if not (found_input and found_output and found_concurrency):
			print "Usage: osm_parser.py --input=INPUT.osm.pbf --output=OUTPUT_NAME --concurrency=x"
			quit()
		
		if not os.path.exists(INPUT):
			print "The input file does not exist or could not be opened."
			quit()

def main(argv):
	checks(argv)
	
	parser_import = __import__('imposm.parser', fromlist = ['imposm'])
	indexer = __import__(('indexing.%s.indexer' % INDEXER), fromlist = ['indexing']).Indexer(OUTPUT)
	nodes = Nodes(indexer)
	ways = Ways()
	coords = Coordinates(ways, indexer)
	
	try:
		print "Indexing nodes and gathering information on ways..."
		
		parser = parser_import.OSMParser(concurrency = CONCURRENCY,
						   nodes_callback = nodes.callback,
						   ways_callback  = ways.callback)
		
		parser.parse(INPUT)
	
		print "Obtaining coordinates for ways and indexing them..."
		
		parser = parser_import.OSMParser(concurrency = CONCURRENCY,
						   coords_callback = coords.callback)
		
		parser.parse(INPUT)
		
		print "Complete."
	except KeyboardInterrupt:
		print "Interrupted. To terminate, hit CTRL+C again and bask in the stack trace shown!"
	
	indexer.stop()
	print str(nodes.counter) + " nodes recorded"
	print str(ways.counter) + " ways recorded"
	

if __name__ == '__main__':
	main(argv[1:])
