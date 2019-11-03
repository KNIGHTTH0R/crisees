#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from api import generate_response, Status_Codes
from db.crisees.models import Event, Query
from urllib2 import unquote
import datetime

'''
Returns a list of query terms for the specified event.
'''
def for_event(request, event_id):
	try:
		return_dict = {}
		queries_dict = {}
		
		event = Event.objects.get(id = event_id)
		queries = Query.objects.filter(event = event)
		
		return_dict['count'] = queries.count()
		return_dict['active_count'] = 0
		
		for query in queries:
			query_entry = {'query'      : query.query,
						   'step'       : query.step,
						   'operator'   : query.operator,
						   'created'    : query.created,
						   'active'     : query.active,
						   'logical_not': query.logical_not,}
			
			if query.active:
				return_dict['active_count'] += 1
			
			queries_dict[query.id] = query_entry
		
		return_dict['terms'] = queries_dict
		return generate_response(return_dict)
	except ObjectDoesNotExist:
		return generate_response({}, status = Status_Codes.NOT_FOUND)

'''
Modifies aspects of a single query.
Can change the operator, whether the query term is active and the query term itself.
Can also delete the term.
'''
@csrf_exempt
def single_query(request, event_id, query_id):
	try:
		event = Event.objects.get(id = event_id)
		query = Query.objects.get(id = query_id)
		
		if query.event != event:
			return generate_response({}, status = Status_Codes.NOT_FOUND)
		
		if request.GET.get('operator') is not None and request.method == 'POST':
			operator = request.GET.get('operator').upper()
			
			if operator == 'AND' or operator == 'OR':
				query.operator = operator
				query.save()
				
				return generate_response({'operator': query.operator.lower()})
			elif operator == 'NOT':
				if query.logical_not:
					query.logical_not = False
				else:
					query.logical_not = True
				
				query.save()
				return generate_response({'logical_not': query.logical_not})
			
			return generate_response({}, status = Status_Codes.NOT_FOUND)
		elif request.GET.get('active') is not None and request.method == 'POST':
			if query.active:
				query.active = False
			else:
				query.active = True
			
			query.save()
			
			active_queries = Query.objects.filter(active = True, event = event)
			return generate_response({'success': True, 'active': query.active, 'active_count': active_queries.count(),})
		elif request.GET.get('delete') is not None and request.method == 'DELETE':
			query.delete()
			
			queries = Query.objects.filter(event = event)
			active_queries = Query.objects.filter(event = event, active = True)
			return generate_response({'success': True, 'total_count': queries.count(), 'active_count': active_queries.count()})
		elif request.GET.get('text') is not None and request.method == 'POST':
			query.query = unquote(request.GET.get('text'))
			query.save()
			
			return generate_response({'success': True,})
		
		return generate_response({}, status = Status_Codes.NOT_FOUND)
	except ObjectDoesNotExist:
		return generate_response({}, status = Status_Codes.NOT_FOUND)

'''
Switches the ordering of a specified query term.
Must also modify the ordering of all other query terms related to the specified event.
'''
@csrf_exempt
def order(request, event_id):
	try:
		event = Event.objects.get(id = event_id)
		
		if request.GET.get('sequence') is None or request.GET.get('sequence') == '' or request.method != 'POST':
			return generate_response({}, status = Status_Codes.NOT_FOUND)
		
		try:
			sequence = list(map(int, request.GET.get('sequence').split(',')))
		except ValueError:
			return generate_response({}, status = Status_Codes.NOT_FOUND)
		
		count = 1
		
		# Loop through all the queries for the specified event, supplying each one with a new step value.
		for query_id in sequence:
			query = Query.objects.get(id = query_id)
			query.step = count
			query.save()
			
			count += 1
		
		return generate_response({'success': True, 'order': sequence})
	
	except ObjectDoesNotExist:
		return generate_response({}, status = Status_Codes.NOT_FOUND)

'''
Adds a query term to the Query model.
CSRF_EXEMPT because this request needs to be a POST.
'''
@csrf_exempt
def add(request, event_id):
	try:
		event = Event.objects.get(id = event_id)
		
		if request.GET.get('query') is None or request.GET.get('query') == '' or request.method != 'POST':
			return generate_response({}, status = Status_Codes.NOT_FOUND)
		
		existing = Query.objects.filter(event = event).order_by('-step')
		
		# Plonk the new query term in at the end of the sequence.
		# Work out the step value based on the step values we currently have.
		if existing.count() == 0:
			step = 1
		else:
			step = existing[0].step + 1
		
		query = Query(event   = event,
					  query   = unquote(request.GET.get('query')),
					  step    = step,
					  created = datetime.datetime.now(),
					  active  = True)
		
		# Save the new query to the model.
		query.save()
		
		# Return information on the newly created query back to the caller.
		# Can be used for validation.
		return_dict = {'id'         : query.id,
					   'event_id'   : query.event.id,
					   'query'      : query.query,
					   'operator'   : query.operator,
					   'step'       : query.step,
					   'created'    : query.created,
					   'active'     : query.active,
					   'logical_not': query.logical_not,}
		
		return generate_response(return_dict)
	# The event specified does not exist!
	except ObjectDoesNotExist:
		return generate_response({}, status = Status_Codes.NOT_FOUND)
