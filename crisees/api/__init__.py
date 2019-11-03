#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, HttpResponseNotFound, HttpResponseServerError
from common import enum
import simplejson
import datetime

API_VERSION = '1.0'
DT_HANDLER = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

# Status codes used within the API.
# Uses the enum imitator defined in the common module.
Status_Codes = enum(
	OK           = 200,
	FORBIDDEN    = 403,
	BAD_REQUEST  = 400,
	NOT_FOUND    = 404,
	SERVER_ERROR = 500,)

# Generates a Django HttpResponse object based on the information provided.
def generate_response(response_dict, status = Status_Codes.OK):
	api_dict = {'api_version': API_VERSION,}
	joined_dict = dict(list(api_dict.items()) + list(response_dict.items()))
	
	if status == Status_Codes.FORBIDDEN:
		return HttpResponseForbidden(simplejson.dumps(joined_dict, default=DT_HANDLER), content_type='application/json')
	elif status == Status_Codes.BAD_REQUEST:
		return HttpResponseBadRequest(simplejson.dumps(joined_dict, default=DT_HANDLER), content_type='application/json')
	elif status == Status_Codes.NOT_FOUND:
		return HttpResponseNotFound(simplejson.dumps(joined_dict, default=DT_HANDLER), content_type='application/json')
	elif status == Status_Codes.SERVER_ERROR:
		return HttpResponseServerError(simplejson.dumps(joined_dict, default=DT_HANDLER), content_type='application/json')
	
	return HttpResponse(simplejson.dumps(joined_dict, default=DT_HANDLER), content_type='application/json')
