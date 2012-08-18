# -*- coding: utf-8 -*-

from django.conf.urls.defaults import url, patterns

urlpatterns = patterns('passbook.views',
    url(r'^webservice/$', 'webservice', name='passbook-webservice'),
)
