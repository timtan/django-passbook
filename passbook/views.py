from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from passbook.models import Pass

def webservice(request, *args, **kwargs):
    return HttpResponse('')

def get_pass(request, id):
    p  = get_object_or_404(Pass, pk=int(id))
    response = HttpResponse(mimetype='application/vnd.apple.pkpass')
    response['Content-Disposition'] = 'attachment; filename=%s.pkpass' % p.type
    z = p.zip(certpath='/path/to/cert', keypath='/path/to/key', passphrase='pass')
    response.write(z)
    return response
