#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import quote
import web.api

def get_list():
	return web.api.get_response("events/", web.api.Methods.GET)

def add(name, longitude, latitude, distance):
	if name == None:
		name = ''
	else:
		name = name.replace(' ', '%20')
	
	if longitude == None:
		longitude = longitude.replace(' ', '%20')
	
	if latitude == None:
		latitude = latitude.replace(' ', '%20')
	
	if distance == None:
		distance = distance.replace(' ', '%20')
	
	url = "events/add/?name=%s&longitude=%s&latitude=%s&distance=%s" % (name, longitude, latitude, distance)
	return web.api.get_response(url, web.api.Methods.POST)
	
def toggle_active(event_id):
	return web.api.get_django_response(("events/%d/active/" % event_id), web.api.Methods.POST)

def get_stream(event_id, start = None, end = None, since = None, media = None, limit = None, time_only = None, query = None, sentiment = None):
	if start == None:
		start = ''
	else:
		start = '&start=' + start
	
	if end == None:
		end = ''
	else:
		end = '&end=' + end
	
	if since == None:
		since = ''
	else:
		since = '&since=' + since
	
	if media == None:
		media = '/'
	else:
		media = '/' + media + '/'
	
	if time_only == None:
		time_only = ''
	else:
		time_only = '&time_only=1'
	
	if limit == None:
		limit = ''
	else:
		limit = '&limit=' + limit
	
	if query == None:
		query = ''
	else:
		query = '&query=' + quote(query.encode('UTF-8'))
	
	if sentiment == None:
		sentiment = ''
	else:
		sentiment = '&sentiment=' + sentiment
	
	return web.api.get_django_response(("streams/%d%s?%s%s%s%s%s%s%s" % (event_id, media, start, end, since, limit, time_only, query, sentiment)), web.api.Methods.GET)
