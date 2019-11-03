#!/usr/bin/env python
# -*- coding: utf-8 -*-

class Ways(object):
	def __init__(self):
		self.counter = 0
		self.references = {}
	
	def callback(self, ways):
		for way in ways:
			if u'highway' in way[1] and u'name' in way[1]:
				for ref in way[2]:
					self.references[ref] = unicode(way[1][u'name'])
				
				self.counter += 1
