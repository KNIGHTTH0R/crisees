#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import quote
import web.api

def get_list_for_event(event_id):
	return web.api.get_response(("queries/%d" % event_id), web.api.Methods.GET)

def modify_operator(event_id, query_id, operator):
	return web.api.get_django_response(("queries/%d/%d/?operator=%s" % (event_id, query_id, operator)), web.api.Methods.POST)

def toggle_active(event_id, query_id):
	return web.api.get_django_response(("queries/%d/%d/?active" % (event_id, query_id)), web.api.Methods.POST)

def delete(event_id, query_id):
	return web.api.get_django_response(("queries/%d/%d/?delete" % (event_id, query_id)), web.api.Methods.DELETE)

def change_text(event_id, query_id, text):
	return web.api.get_django_response(("queries/%d/%d/?text=%s" % (event_id, query_id, quote(text.encode('UTF-8')))), web.api.Methods.POST)

def order(event_id, sequence):
	return web.api.get_django_response(("queries/%d/order/?sequence=%s" % (event_id, sequence)), web.api.Methods.POST)

def add(event_id, query):
	return web.api.get_response(("queries/%d/add/?query=%s" % (event_id, quote(query.encode('UTF-8')))), web.api.Methods.POST)
