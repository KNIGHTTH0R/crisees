#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
	# Admin and root URLs
	(r'^admin/'                                              , include(admin.site.urls)),
	(r'^$'                                                   , 'web.views.main'),
	
	# Event URLs
	(r'^event/add/$'                                         , 'web.views.events.add_event'),
	(r'^event/(?P<event>.*)/active/$'                        , 'web.views.events.toggle_active'),
	(r'^event/(?P<event>.*)/queries/list/$'                  , 'web.views.events.list_queries'),
	(r'^event/(?P<event>.*)/queries/add/$'                   , 'web.views.events.add'),
	(r'^event/(?P<event>.*)/queries/order/$'                 , 'web.views.events.order'),
	(r'^event/(?P<event>.*)/queries/(?P<query_id>\w{0,50})/$', 'web.views.events.query_mod'),
	(r'^event/(?P<event>.*)/queries/$'                       , 'web.views.events.tab_queries'),
	(r'^event/(?P<event>.*)/sources/(?P<source>.*)/$'        , 'web.views.events.source_mod'),
	(r'^event/(?P<event>.*)/sources/$'                       , 'web.views.events.tab_sources'),
	(r'^event/(?P<event>.*)/time/$'                          , 'web.views.events.tab_time'),
	(r'^event/(?P<event>.*)/stream/$'                        , 'web.views.events.stream'),
	
	# Event Tab URL
	(r'^event/(?P<event>.*)/$'                               , 'web.views.events.main'),
	
	# Add URLs
	(r'^add/$'                                               , 'web.views.add.main'),
	
	# About URLs
	(r'^about/$'                                             , 'web.views.about.main'),
)
