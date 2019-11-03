#!/usr/bin/env python
# -*- coding: utf-8 -*-

from operator import itemgetter
#from whoosh.query import Every
from whoosh import qparser
from whoosh.query import NumericRange, And
from whoosh.qparser.dateparse import DateParserPlugin
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings as django_settings
from api import generate_response, Status_Codes
from db.crisees.models import Event, Source
from index.indexing import indexer, reader
from urllib2 import unquote
import datetime
import pytz
import re

DEFAULT_LIMIT = 100

'''
Returns a datetime object in UTC time.
Removes problems of different timezones screwing up calculations.
'''
def get_utc(time):
	tz = pytz.timezone(django_settings.TIME_ZONE)
	d_tz = tz.normalize(tz.localize(time))
	
	utc = pytz.timezone('UTC')
	d_utc = d_tz.astimezone(utc)
	
	return d_utc

'''
Returns a stream of information based on the information supplied both in the URL and querystrings.
'''
def list(request, event_id, media = None):
	try:
		event = Event.objects.get(id = event_id)
		sources = event.sources.filter(active = True)
	except ObjectDoesNotExist:
		return generate_response({}, status = Status_Codes.NOT_FOUND)
	
	start = request.GET.get('start')
	end = request.GET.get('end')
	since = request.GET.get('since')
	limit = request.GET.get('limit')
	time_only = request.GET.get('time_only')
	query = request.GET.get('query')
	sentiment = request.GET.get('sentiment')
	
	new_since = get_utc(datetime.datetime.now())
	new_since = datetime.datetime(new_since.year, new_since.month, new_since.day, new_since.hour, new_since.minute, new_since.second)
	
	# Take each variable from the request and try to convert it to the appropriate type.
	# If we get a problem, we just set it to None to indicate that nothing has been supplied.
	
	if start:
		try:
			start = datetime.datetime.strptime(start, "%Y-%m-%dT%H:%M:%S")
		except ValueError:
			start = None
	
	if end:
		try:
			end = datetime.datetime.strptime(end, "%Y-%m-%dT%H:%M:%S")
		except ValueError:
			end = None
	
	if since:
		try:
			since = datetime.datetime.strptime(since, "%Y-%m-%dT%H:%M:%S")
		except ValueError:
			since = None
	
	if limit:
		try:
			limit = int(limit)
		except ValueError:
			limit = None
	
	if time_only:
		try:
			time_only = bool(time_only)
		except ValueError:
			time_only = False
	else:
		time_only = False
	
	if query:
		query = unquote(query.encode('UTF-8'))
	
	if sentiment:
		acceptable = ['positive', 'negative']
		
		if sentiment not in acceptable:
			sentiment = None
	
	# Get a handle on all the source indexes, then call get_stream to pull information out of the indexes.
	
	indexes = obtain_indexes(sources)
	stream = get_stream(indexes, event, start, end, since, limit, media, time_only, query, sentiment)
	
	# Reverse the stream to get the latest information first.
	stream.reverse()
	
	# Construct a dictionary to return to the caller, then append information related to the request
	# to the dictionary. Finally, send it off.
	return_dict = {'items'     : stream,
				   'since_time': new_since.replace(tzinfo = None),
				   'count'     : len(stream),}
	
	if query:
		return_dict['query'] = query
	
	if limit == None:
		return_dict['stream_limit'] = DEFAULT_LIMIT
	elif limit == 0:
		return_dict['stream_limit'] = 0
	else:
		return_dict['stream_limit'] = limit
	
	return generate_response(return_dict)
	
'''
Returns a list with a handle to all of the valid sourcing indexes currently available.
Each item in the list is a dictionary, containing said handle plus the name and sys_id of the source.
Also includes a settings value, which provides access to the SETTINGS dictionary in the specific source file.
'''
def obtain_indexes(sources):
	indexes = []
	
	for source in sources:
		schema = indexer.index_exists(source.sys_name, indexer.Index_Types.Source)
		settings_import = __import__(('backend.specific.%s' % source.sys_name), fromlist = ['backend.specific'])
		
		if schema:
			source_index = reader.Reader(schema, source.sys_name, indexer.Index_Types.Source)
			indexes.append({'id'      : source.sys_name,
							'name'    : source.name,
							'settings': settings_import.SETTINGS,
							'index'   : source_index,})
	
	return indexes

'''
Returns a list representing a stream based on the information supplied to this function.
'''
def get_stream(indexes, event, start, end, since, limit, media, time_only, query_term, sentiment):
	# Start indexing query by obtaining information related only to the specified event.
	query = NumericRange('event_id', event.id, event.id)
	stream = []
	
	for index in indexes:
		searcher = index['index'].get_searcher()
		
		if query_term:
			query_parser = qparser.QueryParser('body', schema = index['index'].schema, group = qparser.OrGroup)
			query = query & query_parser.parse(unicode(query_term))
		
		if limit == None:
			results = searcher.search(query, sortedby = 'creation_time', reverse = True, limit = DEFAULT_LIMIT)
		elif limit == 0:
			results = searcher.search(query, sortedby = 'creation_time', reverse = True, limit = None)
		else:
			results = searcher.search(query, sortedby = 'creation_time', reverse = True, limit = limit)
		
		for result in results:
			res_dict = dict(result)
			
			if media is not None and media.lower() != index['settings']['media'].lower():
				continue
			
			if index['settings']['media'] == 'text' and sentiment:
				if 'sentiment' in res_dict:
					if sentiment == 'positive' and res_dict['sentiment'] > 0.00:
						pass
					elif sentiment == 'negative' and res_dict['sentiment'] < 0.00:
						pass
					else:
						continue
				else:
					continue
			
			res_dict['source_id'] = index['id']
			res_dict['source_name'] = index['name']
			res_dict['media'] = index['settings']['media']
			
			res_dict['link'] = create_url(index, 'link_identifier', res_dict)
			res_dict['link'] = index['settings']['link'] % (res_dict['link'])
			
			if index['settings']['media'].lower() == 'other':
				res_dict['thumbnail'] = create_url(index, 'thumbnail_identifier', res_dict)
				res_dict['thumbnail'] = index['settings']['thumbnail'] % (res_dict['thumbnail'])
			
			if time_only:
				res_dict = {'creation_time': res_dict['creation_time'],
							'indexing_time': res_dict['indexing_time'],}
			
			if since:
				if res_dict['indexing_time'] >= since:
					stream.append(res_dict)
			elif start and end:
				if res_dict['indexing_time'] >= start and res_dict['indexing_time'] <= end:
					stream.append(res_dict)
			else:
				stream.append(res_dict)
	
	stream = sorted(stream, key = itemgetter('creation_time'))
	return stream

'''
Creates a URL based on the template links in the SETTINGS dictionary for each source.
Used for click-to-view links.
'''
def create_url(index, base, result):
	if base not in index['settings']:
		return None
	
	re_pattern = re.compile(r'(%{1}\w+%{1})+')
	base = index['settings'][base]
	properties = re_pattern.findall(base)
	
	for value in properties:
		obtained = result[value.strip('%')]
		base = base.replace(value, obtained)
	
	return base
