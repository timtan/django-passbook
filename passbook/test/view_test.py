from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client

class UpdateTest(TestCase):

    def setUp(self):
        pass


    def test_PassResource_get_AUTH_SUCCESS_NO_CONTENT(self):
        c   = Client()
        url = reverse('passbook-update-pass', args=['NotAvailable'])
        response = c.get(url)
        assert response.status_code == 404