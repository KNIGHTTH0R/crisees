#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Coordinates(object):
	def __init__(self, ways, indexer):
		self.ways = ways
		self.indexer = indexer
	
	def callback(self, coords):
		for coord in coords:
			if coord[0] in self.ways.references:
				
				send_dict = {
					'item_id'    : unicode(coord[0]),
					'latitude'   : coord[2],
					'longitude'  : coord[1],
					'name'       : unicode(self.ways.references[coord[0]]),
					'place_type' : u'highway',
				}
				
				self.indexer.add(send_dict)
