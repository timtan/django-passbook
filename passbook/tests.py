import subprocess
import os
import json
import zipfile, logging
from StringIO import StringIO

from django.test import TestCase
from django.core.urlresolvers import reverse

from .models import Pass, Signer, Barcode, Device
from .utils import write_tempfile

logger = logging.getLogger('passbook')

SSL_CMD = """openssl req -x509 -nodes -days 365 -subj /C=AU/ST=NSW/L=Sydney/CN=www.example.com -newkey rsa:1024 -keyout %s -out %s"""

class UpdateTest(TestCase):

    def setUp(self):
        pass


    def test_UPDATE_NOT_FOUND_PAGE(self):
        url = reverse('passbook-update-pass', args=['999'])
        logger.debug('resolved uri is %s', url)
        response = self.client.get(url)
        assert response.status_code == 404
class PassTestCase(TestCase):
    '''
    Test the Pass class functionality.
    I.e. Adding and Editing passes etc.
    '''

    def setUp(self):
        self.keyfile = write_tempfile('')
        self.certfile = write_tempfile('')
        cmd = SSL_CMD % (self.keyfile, self.certfile)
        p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
        self.assertIn("writing new private key to '%s'" % self.keyfile, p.stderr.read())

        with open(self.keyfile) as f:
            self.key = f.read()
        with open(self.certfile) as f:
            self.cert = f.read()

        self.assertIn('-----BEGIN RSA PRIVATE KEY-----', self.key)
        self.assertIn('-----BEGIN CERTIFICATE-----', self.cert)

        self.signer = Signer.objects.create(label='label', certificate=self.cert,
                                            private_key=self.key, wwdr_certificate=self.cert)

    def create_pass(self):
        return Pass.objects.create(identifier='abc123',
                                   serial_number='123abc',
                                   organization_name='django-passbook',
                                   team_identifier='pass.foo.bar',
                                   description='desc',
                                   auth_token='4UT#',
                                   barcode=Barcode.objects.create(message='1234', format='PKBarcodeFormatPDF417'),
                                   background_color='rgb(0, 0, 0)',
                                   type='coupon',
                                   pass_signer=self.signer)

    def test_add_pass(self):
        _pass = self.create_pass()
        self.assertIsNotNone(_pass)

    def test_generate_bundle(self):
        _pass = self.create_pass()
        serialized_pass = _pass.serialize()
        bundle = _pass.generate_bundle()
        self.assertEquals(serialized_pass, bundle['pass.json'])

    def test_generate_manifest(self):
        _pass = self.create_pass()
        manifest = _pass.generate_manifest()
        self.assertTrue(isinstance(manifest, str))
        manifest = json.loads(manifest)
        self.assertTrue(isinstance(manifest, dict))
        self.assertTrue('pass.json' in manifest)

    def test_zip(self):
        _pass = self.create_pass()
        s = StringIO(_pass.zip())
        z = zipfile.ZipFile(s)
        contents = z.namelist()
        members = ('pass.json', 'manifest.json', 'signature')
        for member in members:
            self.assertIn(member, contents)

        passjson = z.open('pass.json').read()
        self.assertEquals(_pass.serialize(), passjson)

        manifestjson = z.open('manifest.json').read()
        self.assertEquals(_pass.generate_manifest(), manifestjson)

        signature = z.open('signature').read()
        self.assertEquals(_pass.sign(), signature)

        z.close()
        s.close()

    def tearDown(self):
        os.remove(self.keyfile)
        os.remove(self.certfile)
        self.signer.delete()


class WebServiceTest(TestCase):
    def setUp(self):
        self._pass = Pass.objects.create(identifier='abc123',
                                         serial_number='123abc',
                                         organization_name='django-passbook',
                                         team_identifier='pass.foo.bar',
                                         description='desc',
                                         auth_token='4UT#',
                                         barcode=Barcode.objects.create(message='1234', format='PKBarcodeFormatPDF417'),
                                         background_color='rgb(0, 0, 0)',
                                         type='coupon',
                                         pass_signer=Signer.objects.create(certificate='abc', private_key='123',
                                                                           wwdr_certificate='123'))

        self.url = reverse('passbook-webservice-device-post', kwargs={'version': 'v1',
                                                                      'device_library_id': 'abv123',
                                                                      'pass_type_id': self._pass.identifier,
                                                                      'serial_number': self._pass.serial_number})

    def tearDown(self):
        self._pass.delete()

    def test_is_authorized_decorator_returns_401(self):
        # the decorator should return a 401 when 'HTTP_AUTHORIZATION' is not in request.META
        response = self.client.post(self.url, data='{}', content_type='application/json')
        self.assertEquals(401, response.status_code)

        # the decorator should also return a 401 if the incorrect auth_token is passed in 'HTTP_AUTHORIZATION'
        response = self.client.post(self.url, data='{}', content_type='application/json',
                                    HTTP_AUTHORIZATION='ApplePass not a valid auth token')
        self.assertEquals(401, response.status_code)

    def test_device_register_after_pass_added(self):
        self.assertEquals(0, Device.objects.count())

        post_data = json.dumps({'pushToken': 'pushToken'})
        response = self.client.post(self.url, data=post_data, content_type='application/json',
                                    HTTP_AUTHORIZATION='ApplePass ' + self._pass.auth_token)

        self.assertEquals(200, response.status_code)
        self.assertEquals(1, Device.objects.count())
        device = Device.objects.get()
        self.assertEquals('pushToken', device.push_token)
        self.assertIn(self._pass, device.passes.all())

    def test_unregister_device_from_pass(self):
        device = Device.objects.create(push_token='abc', device_library_id='abv123')
        device.passes.add(self._pass)
        self.assertIn(self._pass, device.passes.all())
        response = self.client.delete(self.url, HTTP_AUTHORIZATION='ApplePass ' + self._pass.auth_token)
        self.assertEquals(200, response.status_code)
        self.assertNotIn(self._pass, device.passes.all())
