#!/usr/bin/env python
# -*- coding: utf-8 -*-

from backend.indexing.schema import Schema as Schema_Base
from backend.sourcing.collector import Collector as Collector_Base
from index.indexing.indexer import to_date
from common.terminal import statuses
from django.conf import settings as django_settings
import datetime
import pytz
import urllib
from whoosh.fields import *
from time import sleep
import gdata.youtube.service

SETTINGS = {
	'developer_key'       : 'AI39si6giE6opdJEt7OEPPhnPAYs8Pb8oveG82vfLCdFgsboBYoeegYdyXpKAncGxYJQIYLD6KetVsExKyTd8hw6fBB8Blbviw',
	'feed_url'            : 'http://gdata.youtube.com/feeds/api/videos/?q=%s&orderby=published&v=2',
	'poll_delay'          : 300,
	'commit_count'        : 1,
	'utc_offset'          : -1,
	'media'               : u'other',
	'thumbnail'           : 'http://img.youtube.com/vi/%s/1.jpg',
	'thumbnail_identifier': '%item_id%',
	'link'                : 'http://youtu.be/%s/',
	'link_identifier'     : '%item_id%',
}

def get_utc(time):
	tz = pytz.timezone(django_settings.TIME_ZONE)
	d_tz = tz.normalize(tz.localize(time))
	
	utc = pytz.timezone('UTC')
	d_utc = d_tz.astimezone(utc)
	
	return d_utc

class Schema(Schema_Base):
	pass

class Collector(Collector_Base):
	
	def __init__(self, scanner):
		super(Collector, self).__init__(scanner, SETTINGS, Schema)
		super(self.__class__, self).run()
	
	def connect(self):
		service = gdata.youtube.service.YouTubeService()
		service.developer_key = 'AI39si6giE6opdJEt7OEPPhnPAYs8Pb8oveG82vfLCdFgsboBYoeegYdyXpKAncGxYJQIYLD6KetVsExKyTd8hw6fBB8Blbviw'
		
		query_list = self.scanner.get_list_str()
		query_list_str = ""
		
		for query in query_list:
			query_list_str += query + "%7C"
		
		query_list_str = query_list_str[:-1]
		
		feed_url = 'http://gdata.youtube.com/feeds/api/videos?vq=%s&orderby=published&max-results=10' % (urllib.quote_plus(query_list_str))
		feed = service.GetYouTubeVideoFeed(feed_url)
		
		return feed.entry
	
	def run(self):
		while True:
			if self.stop_event.isSet() or self.crisis_stop_event.isSet():
				break
			
			if self.scanner.is_empty():
				sleep(1)
			else:
				try:
					since_time = get_utc(datetime.datetime.now())
					
					for item in self.connect():
						body = u""
						
						if item.media.description.text is None:
							body = u""
						else:
							body = item.media.description.text.decode('utf-8')
						
						if item.media.keywords.text is not None:
							body += item.media.keywords.text.decode('utf-8')
						
						send_dict = {
							'since_time'   : since_time,
							'item_id'      : unicode(item.id.text.rsplit('/', 1)[1]),
							'body'         : body,
							'creation_time': datetime.datetime.strptime(item.updated.text, "%Y-%m-%dT%H:%M:%S.000Z"),
							'screen_name'  : item.author[0].name.text.decode('utf-8'),
							'longitude'    : u"",
							'latitude'     : u"",
							# item.geo.location()
						}
						
						self.to_filter(send_dict)
					
					sleep(self.settings['poll_delay'])
				except IOError:
					print statuses.fail(
						"The Youtube API failed.",
						sub = "Terminate the sourcer, check YouTube's settings, and try again.")
					quit()
