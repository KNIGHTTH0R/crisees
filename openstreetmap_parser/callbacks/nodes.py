#!/usr/bin/env python
# -*- coding: utf-8 -*-

# List of place types obtained from
# http://wiki.openstreetmap.org/wiki/Map_Features
# 2011-08-23
TYPES = {
	'construction',
	'emergency',
	'highway',
	'ice_road',
	'junction',
	'overtaking',
	'passing_places',
	'proposed',
	'public_transport',
	'service',
	'traffic_calming',
	'winter_road',
	'barrier',
	'cycleway',
	'tracktype',
	'waterway',
	'lock',
	'tunnel',
	'mooring',
	'intermittent',
	'railway',
	'aeroway',
	'aerialway',
	'power',
	'man_made',
	'leisure',
	'building',
	'amenity',
	'office',
	'shop',
	'craft',
	'emergency',
	'tourism',
	'historic',
	'landuse',
	'military',
	'natural',
	'geological',
	'route',
	'boundary',
	'sport',
	'abutters',
	'place',
}

class Nodes(object):
	def __init__(self, indexer):
		self.counter = 0
		self.indexer = indexer
	
	def callback(self, nodes):
		for node in nodes:
			if 'name' in node[1]:
				
				send_dict = {
					'item_id'   : unicode(node[0]),
					'latitude'  : node[2][1],
					'longitude' : node[2][0],
					'name'      : unicode(node[1]['name']),
				}
				
				for object_type in TYPES:
					if unicode(object_type) in node[1]:
						send_dict['place_type'] = unicode(node[1][object_type])
						break
				
				self.indexer.add(send_dict)
				self.counter += 1
