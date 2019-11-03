#!/usr/bin/env python
# -*- coding: utf-8 -*-

from backend.indexing.schema import Schema as Schema_Base
from backend.sourcing.collector import Collector as Collector_Base
from index.indexing.indexer import to_date
from backend.specific.helpers import tweetstream
from common.terminal import statuses
from whoosh.fields import *
from datetime import datetime
from time import sleep

SETTINGS = {
	'username'       : 'CriseesApp',
	'password'       : 'crisees123',
	'reconnects'     : 3,
	'retry_wait'     : 5,
	'commit_count'   : 1,
	'connect_retry'  : 30,
	'media'          : u'text',
	'link'           : 'http://twitter.com/%s/',
	'link_identifier': '%user_id%/status/%item_id%',
}

class Schema(Schema_Base):
	user_id   = TEXT(stored = True)
	location  = TEXT(stored = True, spelling = True)
	time_zone = TEXT(stored = True, spelling = True)

class Collector(Collector_Base):
	
	def __init__(self, scanner):
		super(Collector, self).__init__(scanner, SETTINGS, Schema)
		super(self.__class__, self).run()
		
		self.last_stop = datetime.now()
	
	def connect(self):
		stream = tweetstream.TrackStream(
			self.settings['username'],
			self.settings['password'],
			self.scanner.get_split_list_str(),
			reconnects = self.settings['reconnects'],
			retry_wait = self.settings['retry_wait'])
		
		return stream
	
	def run(self):
		while True:
			if self.stop_event.isSet() or self.crisis_stop_event.isSet():
				break
			
			if self.scanner.is_empty():
				sleep(1)
			else:
				try:
					stream = self.connect()
					
					for tweet in stream:
						if self.crisis_stop_event.isSet():
							stream.close
							quit()
						
						if self.stop_event.isSet() or self.scanner.has_changed():
							stream.close()
							
							now = datetime.now()
							diff = now - self.last_stop
							print diff
							
							if diff.total_seconds() < 10:
								sleep(10)
							
							self.last_stop = now
							break
						
						if tweet.has_key('text'):
							user_id       = unicode(tweet['user']['id_str'])
							screen_name   = unicode(tweet['user']['screen_name'])
							creation_time = to_date(tweet['created_at'])
							location      = unicode(tweet['user']['location'])
							time_zone     = unicode(tweet['user']['time_zone'])
							longitude     = u""
							latitude      = u""
							
							if isinstance(tweet['geo'], dict) and 'type' in tweet['geo'] and tweet['geo']['type'].lower() == 'point':
								longitude = unicode(tweet['geo']['coordinates'][0])
								latitude  = unicode(tweet['geo']['coordinates'][1])
							
							item_id       = unicode(tweet['id'])
							body          = unicode(tweet['text'])
							
							send_dict = {
								'item_id'      : item_id,
								'body'         : body,
								'creation_time': creation_time,
								'screen_name'  : screen_name,
								'longitude'    : longitude,
								'latitude'     : latitude,
								'user_id'      : user_id,
								'location'     : location,
								'time_zone'    : time_zone,
							}
							
							self.to_filter(send_dict)
					
				except tweetstream.AuthenticationError:
					print statuses.fail(
						"Authentication for accessing the Twitter streaming API failed.",
						sub = "Terminate the backend, check Twitter's settings, and try again.")
					quit()
				except tweetstream.ConnectionError:
					print statuses.fail(
						"Connecting to the Twitter streaming API failed.",
						sub = ("After a grace period of %d seconds, I will try and connect again." % self.settings['connect_retry']),)
					sleep(self.settings['connect_retry'])
