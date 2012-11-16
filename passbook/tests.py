import subprocess
import os
import json
import zipfile
from StringIO import StringIO

from django.test import TestCase

from .models import Pass, Signer, Barcode
from .utils import write_tempfile


SSL_CMD = """openssl req -x509 -nodes -days 365 -subj /C=AU/ST=NSW/L=Sydney/CN=www.example.com -newkey rsa:1024 -keyout %s -out %s"""


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
