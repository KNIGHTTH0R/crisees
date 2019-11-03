#!/usr/bin/env python
# -*- coding: utf-8 -*-

from time import sleep
from common.terminal import statuses
from common import get_project_root
from index.indexing import indexer, reader, writer
from backend.managers.geo import Geo
import os
import re
import threading

class Analysis(threading.Thread):
	
	def __init__(self):
		super(Analysis, self).__init__()
		self.stop_event = threading.Event()
		
		self.sentiment_dict = self.__initialise_sentiment()
		self.sentiment_pattern = re.compile(r'\W+')
		
		self.geo = Geo(analysis_manager = self)
	
	def stop(self):
		self.stop_event.set()
	
	def run(self):
		
		while True:
			if self.stop_event.isSet():
				print statuses.success("Analysis manager successfully terminated.")
				break
			
			sleep(1)
	
	def __initialise_sentiment(self):
		filename = os.path.join(get_project_root(), 'backend/analysis/data/AFINN-111.txt')
		
		try:
			return_dict = dict(map(lambda (w, s): (w, int(s)), [
				ws.strip().split('\t') for ws in open(filename)]))
		except IOError:
			print statuses.fail("Failed to find the specified sentiment data file.", sub = filename)
			return {}
		
		print statuses.success("Sentiment Analysis successfully initialised.")
		return return_dict
