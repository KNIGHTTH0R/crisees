#!/usr/bin/env python
# -*- coding: utf-8 -*-

from backend.analysis.controller import Controller
import threading
import Queue

'''
The analysis component of the backend pipeline.
Spawned in its own thread.
'''
class Analyser(threading.Thread):
	
	def __init__(self, collector, indexer):
		super(Analyser, self).__init__()
		self.__collector = collector
		self.__indexer = indexer
		self.__queue = Queue.Queue()
		self.__controller = Controller(self.__collector.scanner)
	
	def run(self):
		while True:
			if self.__collector.crisis_stop_event.isSet():
				break
			
			if self.__collector.stop_event.isSet() and self.__queue.qsize() == 0 and self.__indexer.qsize() == 0:
				break
			
			try:
				item = self.__queue.get(timeout = 0.01)
				item = self.__controller.parse(item)
				
				# Indicate we've analysed the document
				item['analysed'] = True
				
				# Because add is update_document, we avoid duplicates, unless the ID has been messed with.
				self.__indexer.add(item)
				self.__controller.reset()
			except Queue.Empty:
				continue
	
	def add(self, item):
		self.__queue.put(item)
