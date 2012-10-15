from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from passbook.models import Pass, Barcode
import uuid


def webservice(request, *args, **kwargs):
    return HttpResponse('')


def get_pass(request, id):
    p = get_object_or_404(Pass, pk=int(id))
    response = HttpResponse(mimetype='application/vnd.apple.pkpass')
    response['Content-Disposition'] = 'attachment; filename=%s.pkpass' % p.type
    z = p.zip()
    response.write(z)
    return response


def add_pass(request):
    if request.method == 'POST':
        """"""
    return render(request, 'passbook/add_pass.html', {'pass_types': Pass.PASS_TYPES,
                                                      'transit_types': Pass.TRANSIT_TYPE_CHOICES,
                                                      'suggested_serial_number': uuid.uuid4().get_hex(),
                                                      'suggested_auth_token': uuid.uuid4().get_hex(),
                                                      'barcode_types': Barcode.FORMAT_CHOICES})
