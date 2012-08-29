# -*- coding: utf-8 -*-
import os
import hashlib
import zipfile
from StringIO import StringIO

import M2Crypto

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils import simplejson as json
from django.contrib.sites.models import Site

IMAGE_PATH = os.path.join(settings.MEDIA_ROOT, 'passbook')
IMAGE_TYPE = '.*\.(png|PNG)$'
SITE_DOMAIN = Site.objects.get_current().domain


class Signer(models.Model):
    label = models.CharField('A unique label for this signer', max_length=255,
                             unique=True)
    certificate = models.TextField()
    private_key = models.TextField()
    passphrase = models.CharField('Passphrase for the private key', max_length=100,
                                  blank=True, null=True) # Temporary only - we need a more secure way to store passphrase

    def __unicode__(self):
        return u'%s' % self.label


class Pass(models.Model):
    # Standard keys
    format_version = 1
    identifier = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=255)
    # identifier and serial number should be unique together.
    organization_name = models.CharField(max_length=255)
    team_identifier = models.CharField(max_length=255)
    # Brief description of the pass, used by the iOS accessibility technologies.
    # Don’t try to include all of the data on the pass in its description,
    # just include enough detail to distinguish passes of the same type.
    description = models.CharField(max_length=255)

    # Web service keys
    auth_token = models.CharField(max_length=255)
    # webServiceURL string
    locations = models.ManyToManyField('Location', related_name='passes', blank=True, null=True)
    relevant_date = models.DateTimeField(blank=True, null=True)
    barcode = models.ForeignKey('Barcode', related_name='passes')
    background_color = models.CharField(max_length=20)
    foreground_color = models.CharField(max_length=20, blank=True, null=True)
    label_color = models.CharField(max_length=20, blank=True, null=True)

    # Images: background.png, icon.png, logo.png, thumbnail.png, strip.png
    IMAGE_KWARGS = {'path': IMAGE_PATH,
                    'recursive': True,
                    'match': IMAGE_TYPE,
                    'null': True,
                    'blank': True}

    logo = models.FilePathField('The image displayed on the front of the pass', **IMAGE_KWARGS)
    icon = models.FilePathField('The pass\'s icon', path=IMAGE_PATH, recursive=True, match=IMAGE_TYPE)
    thumbnail_image = models.FilePathField('An additional image displayed on the front of the pass', **IMAGE_KWARGS)
    background_image = models.FilePathField('The image displayed as the background of the front of the pass', **IMAGE_KWARGS)
    strip_image = models.FilePathField('The image displayed as a strip behind the primary fields on the front of the pass', **IMAGE_KWARGS)
    supress_strip_shine = models.NullBooleanField('Supress the shine effect of the strip image')
    logo_text = models.CharField(max_length=255, blank=True, null=True)

    """ Style-Specific Information Keys """
    PASS_TYPES = (('boardingPass', 'boarding pass'),
                  ('coupon', 'coupon'),
                  ('eventTicket', 'event ticket'),
                  ('storeCard', 'store card'),
                  ('generic', 'generic'),)

    type = models.CharField(max_length=50, choices=PASS_TYPES)
    header_fields = models.ManyToManyField('Field', related_name='header+', blank=True, null=True)
    primary_fields = models.ManyToManyField('Field', related_name='primary+')
    secondary_fields = models.ManyToManyField('Field', related_name='secondary+', blank=True, null=True)
    auxiliary_fields = models.ManyToManyField('Field', related_name='aux+', blank=True, null=True)
    back_fields = models.ManyToManyField('Field', related_name='back+', blank=True, null=True)

    pass_signer = models.ForeignKey(Signer)

    # associatedStoreIdentifiers --> array of numbers --> where does it go?
    TRANSIT_TYPE_CHOICES = (('PKTransitTypeAir', 'air'),
                            ('PKTransitTypeTrain', 'train'),
                            ('PKTransitTypeBus', 'bus'),
                            ('PKTransitTypeBoat', 'boat'),
                            ('PKTransitTypeGeneric', 'generic'),)
    transit_type = models.CharField(max_length=20, choices=TRANSIT_TYPE_CHOICES, null=True, blank=True)  # Boarding pass only

    def to_dict(self):
        return {
            'formatVersion': self.format_version,
            'passTypeIdentifier': self.identifier,
            'serialNumber': self.serial_number,
            'teamIdentifier': self.team_identifier,
            'description': self.description,
            'authenticationToken': self.auth_token,
            'webServiceURL': 'https://%s%s' % (SITE_DOMAIN, reverse('passbook-webservice')),
            'barcode': self.barcode.to_dict(),
            'organizationName': self.organization_name,
            'locations': [location.to_dict() for location in self.locations.all()],
            self.type: {
                'headerFields': [field.to_dict() for field in self.header_fields.all()],
                'primaryFields': [field.to_dict() for field in self.primary_fields.all()],
                'secondaryFields': [field.to_dict() for field in self.secondary_fields.all()],
                'backFields': [field.to_dict() for field in self.back_fields.all()]
            }
        }

    def serialize(self):
        return json.dumps(self.to_dict())

    def generate_bundle(self):
        bundle = {
            'pass.json': self.serialize()
        }
        return bundle

    def generate_manifest(self, bundle=None):
        """
        The manifest is a JSON dictionary in a file named manifest.json.
        The keys are paths to files in the pass package, relative to the pass.
        The value of each key is the SHA-1 hash of that file’s contents.
        """
        # bundle = bundle or self.generate_bundle()
        images = (('background_image', 'background@2x.png'),
                  ('icon', 'icon@2x.png'),
                  ('thumbnail_image', 'thumbnail@2x.png'),
                  ('strip_image', 'strip@2x.png'),
                  ('logo', 'logo@2x.png'))

        sha = hashlib.sha1()
        sha.update(self.serialize())

        manifest = {
            'pass.json': sha.hexdigest()
        }
        for attr, image_name in images:
            path = getattr(self, attr)
            if path is not None and path != '':
                low_res_path = path.replace('@2x', '')
                low_res_name = image_name.replace('@2x', '')
                for name, path in ((image_name, path), (low_res_name, low_res_path)):
                    with open(path) as file:
                        sha = hashlib.sha1()
                        sha.update(file.read())
                        manifest[name] = sha.hexdigest()
        return json.dumps(manifest)

    def sign(self, manifest=None):
        manifest = manifest or self.generate_manifest()
        buffer = M2Crypto.BIO.MemoryBuffer(manifest)
        signer = M2Crypto.SMIME.SMIME()
        key = M2Crypto.BIO.MemoryBuffer(str(self.pass_signer.private_key))
        cert = M2Crypto.BIO.MemoryBuffer(str(self.pass_signer.certificate))
        args = [key, cert]
        if self.pass_signer.passphrase:
            args.append(lambda x: self.pass_signer.passphrase)
        signer.load_key_bio(*args)
        p7 = signer.sign(buffer, flags=M2Crypto.SMIME.PKCS7_DETACHED)
        out = M2Crypto.BIO.MemoryBuffer()
        p7.write_der(out)
        signature = out.getvalue()
        return signature


    def zip(self):
        s = StringIO()
        pkpass = zipfile.ZipFile(s, 'a')
        manifest = self.generate_manifest()
        pass_json = self.serialize()
        signature = self.sign()
        pkpass.writestr('manifest.json', manifest)
        pkpass.writestr('pass.json', pass_json)
        pkpass.writestr('signature', signature)


        images = (('background_image', 'background@2x.png'),
                  ('icon', 'icon@2x.png'),
                  ('thumbnail_image', 'thumbnail@2x.png'),
                  ('strip_image', 'strip@2x.png'),
                  ('logo', 'logo@2x.png'))

        for attr, image_name in images:
            path = getattr(self, attr)
            if path is not None and path != '':
                low_res_path = path.replace('@2x', '')
                low_res_name = image_name.replace('@2x', '')
                for name, path in ((image_name, path), (low_res_name, low_res_path)):
                    with open(path) as file:
                        pkpass.writestr(name, file.read())



        for file in pkpass.filelist:
            file.create_system = 0
        pkpass.close()
        s.seek(0)
        return s.read()

    def __unicode__(self):
        return u'%s %s' % (self.type, self.serial_number)

    class Meta:
        verbose_name_plural = 'passes'


class Barcode(models.Model):
    FORMAT_CHOICES = (('PKBarcodeFormatPDF417', 'PDF 417'),
                      ('PKBarcodeFormatQR', 'QR'),
                      ('PKBarcodeFormatAztec', 'Aztec'),
                      ('PKBarcodeFormatText', 'Text'),)

    message = models.CharField(max_length=255)
    format = models.CharField('Barcode format', choices=FORMAT_CHOICES, max_length=50)
    encoding = models.CharField(max_length=50, default='iso-8859-1')
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    def to_dict(self):
        barcode = {
            'message': self.message,
            'format': self.format,
            'messageEncoding': self.encoding
        }
        if self.alt_text is not None:
            barcode['alternativeText'] = self.alt_text
        return barcode

    def __unicode__(self):
        return u'Barcode: %s' % self.message


class Field(models.Model):
    key = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    value = models.TextField()
    text_alignment = models.CharField(max_length=20, blank=True, null=True)
    change_message = models.CharField(max_length=255, blank=True, null=True)
    # Allow date/time styles to be defined if value is a date or time.
    DATE_STYLES = (('PKDateStyleNone', 'PKDateStyleNone'),
                   ('PKDateStyleShort', 'PKDateStyleShort'),
                   ('PKDateStyleMedium', 'PKDateStyleMedium'),
                   ('PKDateStyleLong', 'PKDateStyleLong'),
                   ('PKDateStyleFull', 'PKDateStyleFull'),)

    date_style = models.CharField(max_length=20, blank=True, null=True, choices=DATE_STYLES)
    time_style = models.CharField(max_length=20, blank=True, null=True, choices=DATE_STYLES)
    is_relative = models.NullBooleanField()

    # Allow number style keys if value is a number
    currency_code =  models.CharField(max_length=5, null=True, blank=True)

    NUMBER_STYLES = (('PKNumberStyleDecimal', 'Decimal'),
                     ('PKNumberStylePercent', 'Percentage'),
                     ('PKNumberStyleScientific', 'Scientific'),
                     ('PKNumberStyleSpellOut', 'Spelled Out'),)

    number_style = models.CharField(max_length=20, null=True, blank=True, choices=NUMBER_STYLES)

    def to_dict(self):
        field = {
            'key': self.key,
            'label': self.label,
            'value': self.value
        }
        keys_and_attrs =  (
            ('textAlignment', 'text_alignment'),
            ('changeMessage', 'change_message'),
            ('dateStyle', 'date_style'),
            ('timeStyle', 'time_style'),
            ('isRelative', 'is_relative'),
            ('currencyCode', 'currency_code'),
            ('numberStyle', 'number_style'))

        for key, attr in keys_and_attrs:
            a = getattr(self, attr)
            if a is not None and a != '':
                field[key] = a

        return field

    def __unicode__(self):
        return u'Field: %s' % self.key


class Location(models.Model):
    longitude = models.FloatField()
    latitude = models.FloatField()
    altitude = models.FloatField(null=True)
    relevant_text = models.CharField(max_length=255, blank=True, null=True)

    def to_dict(self):
        location = {'longitude': self.longitude,
                    'latitude': self.latitude}

        if self.altitude is not None:
            location['altitude'] = self.altitude
        if self.relevant_text is not None and self.relevant_text != '':
            location['relevantText'] = self.relevant_text

        return location
