# -*- coding: utf-8 -*-

from django.conf.urls.defaults import url, patterns
from .webservice.resources import Resource, DeviceResource, LogResource, PassResource
from .views import PassView, PassCreationView, UpdateView

device_resource = DeviceResource.as_view()
pass_resource   = PassResource.as_view()
urlpatterns = patterns(
    '',

    url(r'^update/(?P<pk>\d+)/?$', UpdateView.as_view(), name='passbook-update-pass'),
    url(r'^pass/(?P<id>\d+)/?$', PassView.as_view(), name='passbook-get-pass'),
    url(r'^pass/add/?$', PassCreationView.as_view(), name='passbook-add-pass'),

    url(r'^webservice/$', Resource.as_view(), name='passbook-webservice'),

    url(r'^webservice/(?P<version>\w+)/devices/(?P<device_library_id>\w+)/registrations/(?P<pass_type_id>[\w\._-]+)/(?P<serial_number>\w+)$',
        device_resource, name='passbook-webservice-device-post'),

    url(r'^webservice/(?P<version>\w+)/devices/(?P<device_library_id>\w+)/registrations/(?P<pass_type_id>[\w\._-]+)$',
        device_resource, name='passbook-webservice-device-passes'),

    url(r'^webservice/(?P<version>\w+)/passes/(?P<pass_type_id>[\w\._-]+)/(?P<serial_number>\w+)$',
        pass_resource, name='passbook-webservice-device-passes'),

    url(r'^webservice/(?P<version>\w+)/log', LogResource.as_view(), name='passbook-webservice-log'),
)
