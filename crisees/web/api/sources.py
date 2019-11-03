#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web.api

def get_list():
	return web.api.get_response("sources/", web.api.Methods.GET)

def get_event_list(event_id):
	return web.api.get_response(("events/%d/sources/" % event_id), web.api.Methods.GET)

def toggle_source_active(event_id, source):
	return web.api.get_django_response(("events/%d/sources/%s/active/" % (event_id, source)), web.api.Methods.POST)
