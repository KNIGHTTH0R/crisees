#!/usr/bin/env python
# -*- coding: utf-8 -*-

from db.crisees.models import Event
from django.core.exceptions import ObjectDoesNotExist
from whoosh.query import NumericRange, Or, Term
import math

# 0 = No geo data found
# 1 = Definite geo data found
# 2 = Detected geo data found

'''
Calculates the latitude and longitude of a target point, given the originating latitude and longitude,
the distance in kilometres to span from, and the bearing at which to travel.
'''
def destination_coord(latitude, longitude, distance, bearing):
	latitude = math.radians(float(latitude))
	longitude = math.radians(float(longitude))
	distance = distance / 6371.01
	bearing = math.radians(bearing)
	
	destination_latitude = \
		math.asin(math.sin(latitude)
		        * math.cos(distance)
		        + math.cos(latitude)
		        * math.sin(distance)
		        * math.cos(bearing))
	
	destination_longitude = \
		longitude + math.atan2(
				  math.sin(bearing)
				* math.sin(distance)
				* math.cos(latitude),
				  math.cos(distance)
				- math.sin(latitude)
				* math.sin(destination_latitude))
	
	destination_longitude = \
		math.fmod((destination_longitude + 3 * math.pi),
				  (2 * math.pi)) - math.pi
	
	return (math.degrees(destination_latitude),
			math.degrees(destination_longitude))

def generate_query(bl, tl, tr):
	return NumericRange('latitude', bl[0], tl[0]) & NumericRange('longitude', tl[1], tr[1])

def generate_term(query):
	return Term('name', query)

'''
The analysis controller passes the item to this function.
Queries the analysis index for a match, if we get one with a high enough score, we append a latiutude and longitude to the item.
'''
def parse(scanner, item):
	# Definite co-ordinates found; use these.
	if item['latitude'] != "" and item['longitude'] != "":
		item['geographical'] = 1
		return item
	
	# Co-ordinates not present, let's do some searching to see if
	# there's useful geographical information available!
	try:
		event = Event.objects.get(id = item['event_id'])
	except ObjectDoesNotExist:
		item['geographical'] = 0
		return item
	
	bl = destination_coord(event.latitude, event.longitude, event.distance, 225)
	tl = destination_coord(event.latitude, event.longitude, event.distance, 315)
	tr = destination_coord(event.latitude, event.longitude, event.distance, 45)
	
	searcher = scanner.analysis_manager.geo.indexes[event.id].get_searcher()
	
	queries_split = item['body'].split(' ')
	queries = Or(map(generate_term, queries_split))
	
	s = searcher.search(queries, limit = 1)
	
	if len(s) > 0:
		# The index is messed up; the values are in the wrong fields!
		
		if s.score(0) >= 5.5:
			print s[0]['name']
			print item['body']
			print
			
			item['latitude'] = s[0]['longitude']
			item['longitude'] = s[0]['latitude']
			item['geographical'] = 2
			return item
	
	# If we get here, there's nothing useful; so say it!
	item['geographical'] = 0
	return item
