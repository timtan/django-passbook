import json
import datetime, time
import dateutil.parser

from django.views.generic import View
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.conf import settings

from passbook.models import Pass, Device
from .decorators import is_authorized

from ..utils import render_pass
import logging

logger = logging.getLogger('passbook')

class Resource(View):
    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        # Django 1.3 uses request.raw_post_data instead of request.body
        if hasattr(request, 'raw_post_data') and not hasattr(request, 'body'):
            setattr(request, 'body', getattr(request, 'raw_post_data'))
        return super(Resource, self).dispatch(request, *args, **kwargs)


class DeviceResource(Resource):
    model = Device

    def get(self, request, **kwargs):
        device = get_object_or_404(Device, device_library_id=kwargs.get('device_library_id'))

        #Should Be Retrieve from Model
        response_body = {'lastUpdated': datetime.datetime.now().isoformat()}

        if 'tag' in request.GET:
            updated_since = dateutil.parser.parse(request.GET['tag'])
            response_body['serialNumbers'] = [p.serial_number for p in device.passes.filter(update_at__gte=updated_since)]
        else:
            response_body['serialNumbers'] = [p.serial_number for p in device.passes.all()]
        status = 200 if response_body['serialNumbers'] else 204
        return HttpResponse(json.dumps(response_body), status=status)

    @method_decorator(is_authorized)
    def post(self, request, **kwargs):
        _pass = get_object_or_404(Pass, serial_number=kwargs.get('serial_number'))
        data = json.loads(request.body)
        push_token = data.get('pushToken')
        device, created = self.model.objects.get_or_create(push_token=push_token,
                                                           device_library_id=kwargs.get('device_library_id'))
        if not _pass in device.passes.all():
            device.passes.add(_pass)

        return HttpResponse()

    @method_decorator(is_authorized)
    def delete(self, request, **kwargs):
        p = get_object_or_404(Pass, identifier=kwargs['pass_type_id'],
                              serial_number=kwargs['serial_number'])

        device = get_object_or_404(Device, device_library_id=kwargs['device_library_id'])
        if p in device.passes.all():
            device.passes.remove(p)
        return HttpResponse()


class PassResource(Resource):
    model = Pass

    def get(self, request, **kwargs):

        serial_number = kwargs.get('serial_number')
        authorization = request.META.get('HTTP_AUTHORIZATION')


        logger.info('access with serial number: %s authorization: %s', serial_number, authorization)

        if serial_number is  None or authorization is  None:
            return HttpResponse(status=404)

        authorization = authorization.replace('ApplePass', '').strip()

        if not Pass.objects.filter(serial_number=serial_number,
                auth_token=authorization).exists():
            logger.warn('Pass not found with the corresponding auth and serial')

            return HttpResponse(status=404)
        headers = {'last-modified' : str(time.time()) }
        return render_pass(Pass.objects.filter(serial_number=serial_number,
                    auth_token=authorization)[0], **headers)


class LogResource(Resource):
    def post(self, request, **kwargs):
        print request.POST
        return HttpResponse()
