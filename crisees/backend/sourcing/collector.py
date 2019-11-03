#!/usr/bin/env python
# -*- coding: utf-8 -*-

from backend.filtering.filterer import Filterer
import threading

class Collector(threading.Thread):
	
	def __init__(self, scanner, settings, schema):
		super(Collector, self).__init__()
		self.stop_event = threading.Event()
		self.crisis_stop_event = threading.Event()
		self.scanner = scanner
		self.settings = settings
		self.schema = schema()
		
		self.filterer = Filterer(self)
	
	def stop(self):
		self.stop_event.set()
	
	def crisis_stop(self):
		self.crisis_stop_event.set()
	
	def run(self):
		self.filterer.start()
	
	def to_filter(self, item):
		self.filterer.add(item)
