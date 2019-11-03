#!/usr/bin/env python
# -*- coding: utf-8 -*-

from backend.analysis.analyser import Analyser
from index.indexing.writer import Writer
from index.indexing.indexer import Index_Types
from django.conf import settings as django_settings
import threading
import Queue
import pytz
import datetime

def get_utc(time):
	tz = pytz.timezone(django_settings.TIME_ZONE)
	d_tz = tz.normalize(tz.localize(time))
	
	utc = pytz.timezone('UTC')
	d_utc = d_tz.astimezone(utc)
	
	return d_utc

class Indexer(threading.Thread):
	
	def __init__(self, collector):
		super(Indexer, self).__init__()
		self.__collector = collector
		self.__queue = Queue.Queue()
		
		self.__indexer = Writer(self.__collector.schema,
								self.__collector.scanner.source.sys_name,
								Index_Types.Source,
								commit_count = self.__collector.settings['commit_count'])
		
		self.analyser = Analyser(self.__collector, self)
	
	def run(self):
		self.analyser.start()
		
		while True:
			if self.__collector.crisis_stop_event.isSet():
				self.__indexer.commit()
				break
			
			if self.__collector.stop_event.isSet() and self.__queue.qsize() == 0:
				self.__indexer.commit()
				break
			
			if self.__collector.stop_event.isSet():
				if self.__queue.qsize() % 10:
					print str(self.__queue.qsize()) + " items left to index"
			
			try:
				item = self.__queue.get(timeout = 0.01)
				
				if 'analysed' not in item:
					item['analysed'] = False
				
				# Removes the "since time", used to keep track of the time for polling collectors
				if 'since_time' in item:
					del item['since_time']
				
				if 'analysed' not in item or ('analysed' in item and not item['analysed']):
					self.analyser.add(item)
				
				if 'analysed' in item and item['analysed']:
					
					if 'geographical' not in item:
						item['geographical'] = 0
					
					indexing_time = get_utc(datetime.datetime.now())
					indexing_time = datetime.datetime(indexing_time.year, indexing_time.month, indexing_time.day, indexing_time.hour, indexing_time.minute, indexing_time.second)
					item['indexing_time'] = indexing_time
					
					self.__indexer.save(item)
				
			except Queue.Empty:
				continue
	
	def add(self, item):
		self.__queue.put(item)
	
	def qsize(self):
		return self.__queue.qsize()
