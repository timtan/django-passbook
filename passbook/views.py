import uuid

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View

from .models import Pass, Barcode


class PassView(View):
    def get(self, request, *args, **kwargs):
        p = get_object_or_404(Pass, pk=int(kwargs.get('id')))
        response = HttpResponse(mimetype='application/vnd.apple.pkpass')
        response['Content-Disposition'] = 'attachment; filename=%s.pkpass' % p.type
        z = p.zip()
        response.write(z)
        return response


class PassCreationView(View):
    template_name = 'passbook/add_pass.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'passbook/add_pass.html', {'pass_types': Pass.PASS_TYPES,
                                                          'transit_types': Pass.TRANSIT_TYPE_CHOICES,
                                                          'suggested_serial_number': uuid.uuid4().get_hex(),
                                                          'suggested_auth_token': uuid.uuid4().get_hex(),
                                                          'barcode_types': Barcode.FORMAT_CHOICES})

    def post(request):
        return HttpResponse('')
