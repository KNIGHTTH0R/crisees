#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
from operator import itemgetter
import web.api
import web.api.events
import web.api.queries
import web.api.sources

def main(request, event):
	response = web.api.events.get_list()
	
	if web.api.response_ok(response):
		events = response[1]
		event_info = {}
		
		for event_iter in events:
			if event_iter == event:
				treated_name = event_iter
				event_info = events[event_iter]
				break
		
		return render(
			request,
			'tabs/event.html',
			{'treated_name': treated_name,
			 'event': event_info,},
			content_type = 'text/html')
	else:
		return render(
			request,
			'tabs/noapi.html',
			{},
			content_type = 'text/html')

def add_event(request):
	name = request.GET.get('name')
	longitude = request.GET.get('longitude')
	latitude = request.GET.get('latitude')
	distance = request.GET.get('distance')
	
	response = web.api.events.add(name, longitude, latitude, distance)
	
	if int(response[0]['status']) == 598:
		return HttpResponse(status = web.api.Status_Codes.NO_API_CONNECTION)
	elif int(response[0]['status']) == 400:
		return HttpResponse(status = web.api.Status_Codes.BAD_REQUEST)
	
	return web.api.send_response(response[1])

def list_queries(request, event):
	events = web.api.events.get_list()
	
	if web.api.response_ok(events):
		events = events[1]
		
		for event_iter in events:
			if event_iter == event:
				event_id = events[event_iter]['id']
				break
		
		queries = web.api.queries.get_list_for_event(event_id)[1]
		ordered = []
		
		for query in queries['terms']:
			temp = {}
			temp = queries['terms'][query]
			temp['id'] = query
			
			ordered.append(temp)
		
		ordered = sorted(ordered, key = itemgetter('step'))
		count = 0
		return_str = ""
		
		for query in ordered:
			if query['active']:
				separated = query['query'].split(' ')
				subcount = 1
				logical_not = query['logical_not']
				operator = query['operator']
				
				if len(separated) > 1:
					new = []
					for split_query in separated:
						new_dict = {'active'     : True,
									'logical_not': False,
									'query'      : split_query,
									'operator'   : 'OR',
									'in_group'   : True,}
						
						if subcount == 1:
							new_dict['logical_not'] = logical_not
							new_dict['group_start'] = True
						
						if subcount == len(separated):
							new_dict['operator'] = operator
							new_dict['group_end'] = True
						
						new.append(new_dict)
						subcount += 1
					
					ordered.pop(count)
					subcount = 0
					
					for new_query in new:
						ordered.insert(count + subcount, new_query)
						subcount += 1
			
			count += 1
		
		count = 0
		
		for query in ordered:
			count += 1
			
			if query['active']:
				if query['logical_not']:
					return_str += "<li class='operator'>NOT</li>"
				
				if 'group_start' in query:
					return_str += "<li class='right'>" + query['query'] + "</li>"
				elif 'group_end' in query:
					return_str += "<li class='left'>" + query['query'] + "</li>"
				elif 'in_group' in query:
					return_str += "<li class='group'>" + query['query'] + "</li>"
				else:
					return_str += "<li>" + query['query'] + "</li>"
				
				if count != len(ordered):
					return_str += "<li class='operator'>" + query['operator'] + "</li>"
		
		return HttpResponse(return_str)
	
	return HttpResponse(status = web.api.Status_Codes.NO_API_CONNECTION)

def tab_queries(request, event):
	response = web.api.events.get_list()
	
	if web.api.response_ok(response):
		events = response[1]
		
		for event_iter in events:
			if event_iter == event:
				event_id = events[event_iter]['id']
				break
		
		queries = web.api.queries.get_list_for_event(event_id)[1]
		ordered = []
		
		for query in queries['terms']:
			temp = {}
			temp = queries['terms'][query]
			temp['id'] = query
			
			ordered.append(temp)
		
		ordered = sorted(ordered, key = itemgetter('step'))
		queries['terms'] = ordered
		
		return render(
			request,
			'modal/queries.html',
			{'event_id': event_id,
			 'queries' : queries,
			},
			content_type = 'text/html')
	
	return HttpResponse(status = web.api.Status_Codes.NO_API_CONNECTION)

def tab_sources(request, event):
	response = web.api.events.get_list()
	
	if web.api.response_ok(response):
		events = response[1]
		
		for event_iter in events:
			if event_iter == event:
				event_id = events[event_iter]['id']
				break
		
		sources = web.api.sources.get_list()[1]
		
		for key, value in sources.items():
			if sources[key]['active']:
				del sources[key]['active']
			else:
				del sources[key]
		
		keys = sources.keys()
		keys.sort()
		sources_sorted = map(sources.get, keys)
		
		event_sources = web.api.sources.get_event_list(event_id)[1]
		
		for source in sources_sorted:
			if source['id'] in event_sources:
				source['active'] = True
			else:
				source['active'] = False
		
		return render(
			request,
			'modal/sources.html',
			{'event_id': event_id,
			 'sources' : sources_sorted},
			content_type = 'text/html')
	
	return HttpResponse(status = web.api.Status_Codes.NO_API_CONNECTION)

def tab_time(request, event):
	response = web.api.events.get_list()
	
	if web.api.response_ok(response):
		events = response[1]
		
		for event_iter in events:
			if event_iter == event:
				event_id = events[event_iter]['id']
				break
		
		return render(
			request,
			'modal/time.html',
			{'event_id': event_id,},
			content_type = 'text/html')
	
	return HttpResponse(status = web.api.Status_Codes.NO_API_CONNECTION)

def toggle_active(request, event):
	response = web.api.events.get_list()
	
	if web.api.response_ok(response):
		events = response[1]
		
		for event_iter in events:
			if event_iter == event:
				event_id = events[event_iter]['id']
				break
		
		return web.api.events.toggle_active(event_id)
	
	return HttpResponse(status = web.api.Status_Codes.NO_API_CONNECTION)

def query_mod(request, event, query_id):
	events = web.api.events.get_list()
	
	if web.api.response_ok(events):
		events = events[1]
		
		for event_iter in events:
			if event_iter == event:
				event_id = events[event_iter]['id']
				break
		
		if request.GET.get('operator') is not None:
			return web.api.queries.modify_operator(event_id, int(query_id), request.GET.get('operator'))
		elif request.GET.get('active') is not None:
			return web.api.queries.toggle_active(event_id, int(query_id))
		elif request.GET.get('delete') is not None:
			return web.api.queries.delete(event_id, int(query_id))
		elif request.GET.get('text') is not None:
			return web.api.queries.change_text(event_id, int(query_id), request.GET.get('text'))
		
		return HttpResponse(status = web.api.Status_Codes.NOT_FOUND)
	
	return HttpResponse(status = web.api.Status_Codes.NO_API_CONNECTION)

def order(request, event):
	events = web.api.events.get_list()
	
	if web.api.response_ok(events):
		events = events[1]
		
		for event_iter in events:
			if event_iter == event:
				event_id = events[event_iter]['id']
				break
		
		if request.GET.get('sequence') is not None:
			return web.api.queries.order(event_id, request.GET.get('sequence'))
		
		return HttpResponse(status = web.api.Status_Codes.NOT_FOUND)
	
	return HttpResponse(status = web.api.Status_Codes.NO_API_CONNECTION)

def add(request, event):
	events = web.api.events.get_list()
	
	if web.api.response_ok(events):
		events = events[1]
		
		for event_iter in events:
			if event_iter == event:
				event_id = events[event_iter]['id']
				break
		
		if request.GET.get('query') is not None:
			query = web.api.queries.add(event_id, request.GET.get('query'))[1]
			
			return render(
				request,
				'modal/helpers/query_term.html',
				{'event_id': query['event_id'],
				 'query': query,},
				content_type = 'text/html')
		
		return HttpResponse(status = web.api.Status_Codes.NOT_FOUND)
		
	return HttpResponse(status = web.api.Status_Codes.NO_API_CONNECTION)

def source_mod(request, event, source):
	events = web.api.events.get_list()
	
	if web.api.response_ok(events):
		events = events[1]
		
		for event_iter in events:
			if event_iter == event:
				event_id = events[event_iter]['id']
				break
		
		return web.api.sources.toggle_source_active(event_id, source)
	
	return HttpResponse(status = web.api.Status_Codes.NO_API_CONNECTION)

def stream(request, event):
	events = web.api.events.get_list()
	
	if web.api.response_ok(events):
		events = events[1]
		
		for event_iter in events:
			if event_iter == event:
				event_id = events[event_iter]['id']
				break
		
		start = request.GET.get('start')
		end = request.GET.get('end')
		since = request.GET.get('since')
		limit = request.GET.get('limit')
		time_only = request.GET.get('time_only')
		query = request.GET.get('query')
		sentiment = request.GET.get('sentiment')
		
		return web.api.events.get_stream(event_id, start = start, end = end, since = since, limit = limit, time_only = time_only, query = query, sentiment = sentiment)
	
	return HttpResponse(status = web.api.Status_Codes.NO_API_CONNECTION)
