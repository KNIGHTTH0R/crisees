#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpResponse
import web.api
import web.api.events

def main(request):
	
	return render(
		request,
		'tabs/about.html',
		{},
		content_type = 'text/html')
