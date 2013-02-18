import uuid

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import View, DetailView
from utils import render_pass
from .models import Pass, Barcode


class UpdateView(DetailView):
    model        = Pass
    template_name = 'passbook/admin/notification_updated.html'
    context_object_name = 'pass'

    def get_object(self):
        object = super(UpdateView, self).get_object()
        self.updated_tokens = list(object.notify())
        return object
    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context['updated_tokens'] = self.updated_tokens
        return context

class PassView(View):


    def get(self, request, *args, **kwargs):
        p = get_object_or_404(Pass, pk=int(kwargs.get('id')))
        response = render_pass(p)
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
