# -*- coding: utf-8 -*-

from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('passbook.views',
    url(r'^webservice/$', 'webservice', name='passbook-webservice'),
    url(r'^pass/(?P<id>\d+)/?$', 'get_pass', name='passbook-get-pass'),
    url(r'^pass/add/?$', 'add_pass', name='passbook-add-pass'),
)
