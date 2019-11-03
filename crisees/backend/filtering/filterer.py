#!/usr/bin/env python
# -*- coding: utf-8 -*-

from backend.filtering.controller import Controller
from backend.indexing.indexer import Indexer
import threading
import Queue

class Filterer(threading.Thread):
	
	def __init__(self, collector):
		super(Filterer, self).__init__()
		self.__collector = collector
		self.__queue = Queue.Queue()
		self.__controller = Controller(self.__collector.scanner)
		
		self.indexer = Indexer(self.__collector)
		self.indexer.start()
	
	def run(self):
		while True:
			if self.__collector.crisis_stop_event.isSet():
				break
			
			if self.__collector.stop_event.isSet() and self.__queue.qsize() == 0:
				break
			
			try:
				item = self.__queue.get(timeout = 0.01)
				item = self.__controller.parse(item)
				
				if item is not None:
					self.indexer.add(item)
				
				self.__controller.reset()
			except Queue.Empty:
				continue
	
	def add(self, item):
		self.__queue.put(item)
