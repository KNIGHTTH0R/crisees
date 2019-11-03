#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
	# Source URLs
	(r'^sources/$'                                                    , 'api.responses.sources.list_all'),
	(r'^sources/all/$'                                                , 'api.responses.sources.list_all'),
	
	# Event URLs
	(r'^events/$'                                                     , 'api.responses.events.list_all'),
	(r'^events/all/$'                                                 , 'api.responses.events.list_all'),
	(r'^events/add/$'                                                 , 'api.responses.events.add'),
	(r'^events/(?P<event_id>\w{0,50})/active/$'                       , 'api.responses.events.toggle_active'),
	(r'^events/(?P<event_id>\w{0,50})/sources/(?P<source>.*)/active/$', 'api.responses.events.toggle_source'),
	(r'^events/(?P<event_id>\w{0,50})/sources/$'                      , 'api.responses.events.list_sources'),
	(r'^events/(?P<event_id>\w{0,50})/$'                              , 'api.responses.events.single'),
	
	# Query URLs
	(r'^queries/(?P<event_id>\w{0,50})/add/$'                         , 'api.responses.queries.add'),
	(r'^queries/(?P<event_id>\w{0,50})/order/$'                       , 'api.responses.queries.order'),
	(r'^queries/(?P<event_id>\w{0,50})/(?P<query_id>\w{0,50})/$'      , 'api.responses.queries.single_query'),
	(r'^queries/(?P<event_id>\w{0,50})/$'                             , 'api.responses.queries.for_event'),
	
	# Stream URLs
	(r'^streams/(?P<event_id>\w{0,50})/(?P<media>.*)/$'               , 'api.responses.streams.list'),
	(r'^streams/(?P<event_id>\w{0,50})/$'                             , 'api.responses.streams.list'),
)

handler404 = 'api.responses.errors.not_found'
handler500 = 'api.responses.errors.server_error'
