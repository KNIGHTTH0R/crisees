#!/usr/bin/env python
# -*- coding: utf-8 -*-

import simplejson
from api import generate_response, Status_Codes

# Called by the error handler if the specified resource is not found.
# Returns a HttpResponse object with status 404.
def not_found(request):
	
	info = {'error_code': 404,
			'info'      : 'The requested resource was not found.',
			'path'      : request.path,}
	
	return generate_response(info, status = Status_Codes.NOT_FOUND)

# Called by the error handler if the server encounters an error.
# Returns a HttpResponse object with status 500.
def server_error(request):
	
	info = {'error_code': 500,
			'info'      : 'An internal server error occured.',
			'path'      : request.path,}
	
	return generate_response(info, status = Status_Codes.SERVER_ERROR)
