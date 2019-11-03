#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
import web.api
import web.api.events

def main(request):
	events = web.api.events.get_list()
	
	if web.api.response_ok(events):
		ordered = []
		
		for key in sorted(events[1].iterkeys()):
			events[1][key]['tab_url'] = key
			ordered.append(events[1][key])
		
		return render(
			request,
			'body.html',
			{'events': ordered},
			content_type = 'text/html')
	
	return render(
		request,
		'body.html',
		{'noapi': True,},
		content_type = 'text/html')
