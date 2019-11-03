#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotFound, HttpResponseServerError
from httplib2 import Http
from urllib import urlencode
from common import enum
import simplejson

COMPATIBLE_VERSION = '1.0'
API_BASE_URL = 'http://127.0.0.1:8001/'
DT_HANDLER = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
http_object = Http()

Methods = enum(
	GET    = 'GET',
	POST   = 'POST',
	DELETE = 'DELETE',)

Status_Codes = enum(
	OK                = 200,
	FORBIDDEN         = 403,
	BAD_REQUEST       = 400,
	NOT_FOUND         = 404,
	SERVER_ERROR      = 500,
	NO_API_CONNECTION = 598,
	INCOMPATIABLE_API = 599,)

def get_response(api_path, method, data = {}, recreate = False):
	global http_object
	
	if recreate:
		http_object = Http()
	
	try:
		response = http_object.request(API_BASE_URL + api_path, method, urlencode(data))
	except:
		if not recreate:
			return get_response(api_path, method, data = data, recreate = True)
		
		return ({'status': str(Status_Codes.NO_API_CONNECTION),}, {})
	
	as_dict = simplejson.loads(response[1])
	
	if 'api_version' in as_dict and as_dict['api_version'] == COMPATIBLE_VERSION:
		del as_dict['api_version']
		return (response[0], as_dict)
	else:
		return ({'status': str(Status_Codes.INCOMPATIABLE_API),}, {})

def send_response(data):
	return HttpResponse(simplejson.dumps(data, default=DT_HANDLER), content_type='application/json')

def response_ok(response):
	if int(response[0]['status']) == Status_Codes.OK:
		return True
	
	return False

def get_django_response(api_path, method, data = {}):
	response = get_response(api_path, method, data)
	status = int(response[0]['status'])
	
	if status == Status_Codes.BAD_REQUEST:
		return HttpResponseBadRequest(simplejson.dumps(response[1], default=DT_HANDLER), content_type='application/json')
	elif status == Status_Codes.FORBIDDEN:
		return HttpResponseForbidden(simplejson.dumps(response[1], default=DT_HANDLER), content_type='application/json')
	elif status == Status_Codes.NOT_FOUND:
		return HttpResponseNotFound(simplejson.dumps(response[1], default=DT_HANDLER), content_type='application/json')
	elif status == Status_Codes.SERVER_ERROR:
		return HttpResponseServerError(simplejson.dumps(response[1], default=DT_HANDLER), content_type='application/json')
	
	return HttpResponse(simplejson.dumps(response[1], default=DT_HANDLER), content_type='application/json')
