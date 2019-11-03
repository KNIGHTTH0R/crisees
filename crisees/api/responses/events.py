#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from api import generate_response, Status_Codes
from db.crisees.models import Event, Source
from backend.managers.geo import Geo
from threading import Thread
import datetime

'''
Converts spaces within an event name to underscores.
Used to represent the event in the "hash" portion of the URL.
'''
def get_tab_name(event_name):
	return event_name.lower().replace(' ', '_')

'''
Returns a JSON response containing all current events.
'''
def list_all(request):
	events_dict = {}
	
	for event in Event.objects.all():
		event_dict = {'id'       : event.id,
					  'name'     : event.name,
					  'active'   : event.active,
					  'created'  : event.created,
					  'latitude' : event.latitude,
					  'longitude': event.longitude,
					  'distance' : event.distance,}
		
		events_dict[get_tab_name(event.name)] = event_dict
	
	return generate_response(events_dict)

'''
Attempts to create a new event based on querystrings provided in the request.
CSRF_EXEMPT as resquest must have POST method.
'''
@csrf_exempt
def add(request):
	if request.method == 'POST':
		try:
			# Attempt to read and convert the information from the request to the relevant type.
			# Fails if information is missing, or of the wrong type.
			name = request.GET.get('name')
			longitude = float(request.GET.get('longitude'))
			latitude = float(request.GET.get('latitude'))
			distance = int(request.GET.get('distance'))
		except TypeError:
			return generate_response({}, status = Status_Codes.BAD_REQUEST)
		except ValueError:
			return generate_response({}, status = Status_Codes.BAD_REQUEST)
		
		try:
			# Attempt to pick an event that has the same name.
			# Fails if no event exists.
			previous = Event.objects.get(name = name)
			return generate_response({}, status = Status_Codes.BAD_REQUEST)
		except ObjectDoesNotExist:
			# Clever! Use the catch to create a new event; we know that an event with
			# the same name doesn't already exist.
			new_event = Event(name      = name,
							  longitude = longitude,
							  latitude  = latitude,
							  distance  = distance,
							  active    = True,
							  created   = datetime.datetime.now())
			
			new_event.save()
			
			# Spawn a new thread to create the geographical index for the new event.
			# Currently joins so it's pointles, but will be eventually taken out.
			index_thread = Thread(target = add_index, args = (new_event, ))
			index_thread.start()
			index_thread.join()
			
			return generate_response({'event_id': new_event.id,
									  'tab_url' : get_tab_name(new_event.name),
									  'name'    : new_event.name,
									  'active'  : new_event.active,})
	else:
		return generate_response({}, status = Status_Codes.NOT_FOUND)

'''
Function called by add() to create a new geographical index for a new event.
Spawned in a separate thread.
'''
def add_index(new_event):
	geo_object = Geo(check_all = False)
	geo_object.check_event_index(new_event)

# To be fixed
def single(request, event_id):
	try:
		event = Event.objects.get(id = event_id)
		
		event_dict = {'id'       : event.id,
					  'name'     : event.name,
					  'active'   : event.active,
					  'created'  : event.created,
					  'latitude' : event.latitude,
					  'longitude': event.longitude,
					  'distance' : event.distance,}
		
		return generate_response({'event': event_dict,})
	except ObjectDoesNotExist:
		return generate_response({}, status = Status_Codes.NOT_FOUND)

'''
Toggles the active flag of an event, denoted by event_id.
Accepts only POST requests. All other requests are invalid, and will
result in a HTTP 403 status.

If an unrecognised event ID is supplied, a HTTP 404 status will result.

For valid event ID's, a dictionary is returned containing the event ID
and the new active flag value.
'''
@csrf_exempt
def toggle_active(request, event_id):
	
	if request.method == 'POST':
		try:
			event = Event.objects.get(id = event_id)
			
			if event.active:
				event.active = False
			else:
				event.active = True
			
			event.save()
			
			response = {'id': event.id,
						'active': event.active,}
			
			return generate_response(response)
			
		except ObjectDoesNotExist:
			return generate_response({}, status = Status_Codes.NOT_FOUND)
	
	return generate_response({}, status = Status_Codes.FORBIDDEN)

'''
Returns a list of all the sources for the specified event.
If the event specified does not exist, fails gracefully.
'''
def list_sources(request, event_id):
	try:
		event = Event.objects.get(id = event_id)
		sources = event.sources.filter(active = True)
		
		return_dict = {}
		
		for source in sources:
			temp = {'id'  : source.sys_name,
					'name': source.name,}
			
			return_dict[source.sys_name] = temp
		
		return generate_response(return_dict)
	except ObjectDoesNotExist:
		return generate_response({}, status = Status_Codes.NOT_FOUND)

'''
Adds/removes a source from the specified event.
CSRF_EXEMPT as this request must have a POST method.
If the specified event/source does not exist, fails gracefully.
'''
@csrf_exempt
def toggle_source(request, event_id, source):
	try:
		if request.method == 'POST':
			event = Event.objects.get(id = event_id)
			selected = Source.objects.get(sys_name = source)
			event_sources = event.sources.all()
			
			if selected in event_sources:
				event.sources.remove(selected)
				return generate_response({'id'    : selected.sys_name,
										  'active': False,})
			else:
				event.sources.add(selected)
				return generate_response({'id'    : selected.sys_name,
										  'active': True,})
		
		return generate_response({}, status = Status_Codes.FORBIDDEN)
	except ObjectDoesNotExist:
		return generate_response({}, status = Status_Codes.NOT_FOUND)
