#!/usr/bin/env python
# -*- coding: utf-8 -*-

from index.indexing import indexer, reader, writer
from common.terminal import statuses
from time import sleep
import threading

class Geo(object):
	
	def __init__(self, check_all = True, analysis_manager = None):
		self.schema = indexer.index_exists('geo', indexer.Index_Types.Crisees)
		self.indexes = {}
		
		if self.schema:
			print statuses.success("Geographical Analysis successfully initialised.")
			self.__reader = reader.Reader(self.schema, 'geo', indexer.Index_Types.Crisees)
			
			if check_all:
				from db.crisees.models import Event
				
				for event in Event.objects.all():
					self.indexes[event.id] = self.check_event_index(event)
		else:
			print statuses.fail("Failed to find the geographical places index.", "Geographical analysis will not work for this session.")
			self.__reader = None
		
		if analysis_manager is not None:
			self.verifier = Verifier(self, analysis_manager)
			self.verifier.start()
	
	def check_event_index(self, event):
		from backend.analysis.pipe.geo import destination_coord, generate_query
		
		if indexer.index_exists('geo.' + str(event.id), indexer.Index_Types.Crisees):
			print statuses.info(("Geographical index for event '%s' found." % (event.name)))
		else:
			# Inform the end user what is happening
			print statuses.info(("Creating geographical index for the event '%s'" % (event.name)), sub = "This will take a minute; please wait.")
			
			# Set up the writer objects for this event
			event_writer = writer.Writer(self.schema, 'geo.' + str(event.id), indexer.Index_Types.Crisees, commit_count = None)
			
			# Set up box for the event, and retrieve data from master index
			master_searcher = self.__reader.get_searcher()
			
			bl = destination_coord(event.latitude, event.longitude, event.distance, 225)
			tl = destination_coord(event.latitude, event.longitude, event.distance, 315)
			tr = destination_coord(event.latitude, event.longitude, event.distance, 45)
			
			query = generate_query(bl, tl, tr)
			results = master_searcher.search(query, limit = None)
			
			for result in results:
				event_writer.save({'latitude': result['latitude'],
								   'longitude': result['longitude'],
								   'name': result['name'],})
			
			event_writer.commit()
			event_writer.index.close()
		
		# Return a Reader object for the index
		return reader.Reader(self.schema, 'geo.' + str(event.id), indexer.Index_Types.Crisees)

class Verifier(threading.Thread):
	
	def __init__(self, parent, analysis_manager):
		super(Verifier, self).__init__()
		self.__parent = parent
		self.__stop_event = analysis_manager.stop_event
	
	def run(self):
		from db.crisees.models import Event
		self.__event_list = Event.objects.all()
		
		while True:
			if self.__stop_event.isSet():
				print "Verifier killed"
				break
			
			current = Event.objects.all()
			difference = list(set(current) - set(self.__event_list))
			
			if len(difference) > 0:
				for event in difference:
					print "Need to add event %s to the list" % (event.name)
					
					try:
						writer.Writer(self.__parent.schema, 'geo.' + str(event.id), indexer.Index_Types.Crisees, commit_count = None)
						
						print "Success, got the lock. Adding to the event list in the backend"
						print
						
						self.__parent.indexes[event.id] = self.__parent.check_event_index(event)
						self.__event_list = current
					except:
						print "Couldn't get lock this time around, will try again."
						print
						break
				
			sleep(1)
