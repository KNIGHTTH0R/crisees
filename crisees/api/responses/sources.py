#!/usr/bin/env python
# -*- coding: utf-8 -*-

from api import generate_response
from db.crisees.models import Source

'''
Returns a JSON response containing all sources, and their current status.
'''
def list_all(request):
	streams_dict = {}
	
	for source in Source.objects.all():
		source_dict = {'id'    : source.sys_name,
					   'name'  : source.name,
					   'active': source.active,}
		
		streams_dict[source.sys_name] = source_dict
	
	return generate_response(streams_dict)
