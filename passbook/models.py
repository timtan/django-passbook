# -*- coding: utf-8 -*-
import os
import hashlib
import zipfile
from StringIO import StringIO
import subprocess

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
import json
from django.contrib.sites.models import Site
import logging
from .utils import write_tempfile, to_time_stamp

IMAGE_PATH = os.path.join(settings.MEDIA_ROOT, 'passbook')
IMAGE_TYPE = '.*\.(png|PNG)$'

SSL_ARGS = '''openssl smime -binary -sign -signer %(cert)s -inkey %(key)s -in %(manifest)s -outform DER -certfile %(wwdr_cert)s'''

logger = logging.getLogger('passbook')


class Signer(models.Model):
    label = models.CharField('A unique label for this signer', max_length=255,
                             unique=True)
    certificate = models.TextField()
    private_key = models.TextField()
    wwdr_certificate = models.TextField('Apple WWDR intermediate certificate')
    passphrase = models.CharField('Passphrase for the private key', max_length=100,
                                  blank=True, null=True)  # Temporary only - we need a more secure way to store passphrase

    def __unicode__(self):
        return self.label


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

    # relevancy
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
    supress_strip_shine = models.BooleanField('Supress the shine effect of the strip image', default=False)
    logo_text = models.CharField(max_length=255, blank=True, null=True)

    enable_web_service = models.BooleanField("Whether to enable web service", default=False)
    """ Style-Specific Information Keys """
    PASS_TYPES = (('boardingPass', 'boarding pass'),
                  ('coupon', 'coupon'),
                  ('eventTicket', 'event ticket'),
                  ('storeCard', 'store card'),
                  ('generic', 'generic'),)

    type = models.CharField(max_length=50, choices=PASS_TYPES)
    pass_signer = models.ForeignKey(Signer)

    # associatedStoreIdentifiers --> array of numbers --> where does it go?
    TRANSIT_TYPE_CHOICES = (('PKTransitTypeAir', 'air'),
                            ('PKTransitTypeTrain', 'train'),
                            ('PKTransitTypeBus', 'bus'),
                            ('PKTransitTypeBoat', 'boat'),
                            ('PKTransitTypeGeneric', 'generic'),)
    transit_type = models.CharField(max_length=20, choices=TRANSIT_TYPE_CHOICES, null=True, blank=True)  # Boarding pass only

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def to_dict(self):
        d = {
            'formatVersion': self.format_version,
            'passTypeIdentifier': self.identifier,
            'serialNumber': self.serial_number,
            'teamIdentifier': self.team_identifier,
            'description': self.description,
            'barcode': self.barcode.to_dict(),
            'organizationName': self.organization_name,
            'locations': [location.to_dict() for location in self.locations.all()],
            self.type: {
                'headerFields': [field.to_dict() for field in self.fields.filter(field_type='header').order_by('priority')],
                'primaryFields': [field.to_dict() for field in self.fields.filter(field_type='primary').order_by('priority')],
                'secondaryFields': [field.to_dict() for field in self.fields.filter(field_type='secondary').order_by('priority')],
                'auxiliaryFields': [field.to_dict() for field in self.fields.filter(field_type='auxiliary').order_by('priority')],
                'backFields': [field.to_dict() for field in self.fields.filter(field_type='back').order_by('priority')]
            },
            'backgroundColor': self.background_color
        }

        if self.enable_web_service :

            address =  getattr(settings, 'WEBSERVICE_ADDRESS', "")
            if not address:
                address = Site.objects.get_current().domain
                logger.info('web service address is set from database %s', address)
            else:
                logger.info('web service address is set from config: %s', address)


            auth_token      = self.auth_token
            web_service_url = '%s://%s%s' % ('http' if getattr(settings, 'DEBUG', False) else 'https',
                                             address,
                                             reverse('passbook-webservice'))

            logger.debug('web service is added token %s, url %s', auth_token, web_service_url)
            web_service_extra = {
                'authenticationToken': auth_token,
                'webServiceURL': web_service_url,
            }
            d.update(web_service_extra)

        if self.foreground_color:
            d['foregroundColor'] = self.foreground_color

        if self.type == 'boardingPass':
            d['boardingPass']['transitType'] = self.transit_type

        if self.relevant_date :
            d['relevantDate'] = to_time_stamp(self.relevant_date)

        optional_images = (('logo', self.logo),
                           ('thumbnailImage', self.thumbnail_image),
                           ('stripImage', self.strip_image),
                           ('backgroundImage', self.background_image))

        for attr_name, attr in optional_images:
            if attr:
                d[attr_name] = attr

        if self.logo_text is not None:
            d['logoText'] = self.logo_text

        return d

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
                    try:
                        with open(path) as file:
                            sha = hashlib.sha1()
                            sha.update(file.read())
                            manifest[name] = sha.hexdigest()
                    except IOError as e:
                        logger.warn('file %s not available', path)
        return json.dumps(manifest)

    def sign(self, manifest=None):
        manifest = manifest or self.generate_manifest()

        # TODO: More elegant solution than tempfile.mkstemp()
        # However, the tempfile.mkstemp() approach allows us to
        # use more than one key/cert pair rather than adding the
        # key and cert to the file path and specifying in settings.
        keyfile = write_tempfile(self.pass_signer.private_key)
        certfile = write_tempfile(self.pass_signer.certificate)
        wwdr_certfile = write_tempfile(self.pass_signer.wwdr_certificate)
        manifest_file = write_tempfile(manifest)

        args = SSL_ARGS % {'cert': certfile,
                           'key': keyfile,
                           'manifest': manifest_file,
                           'wwdr_cert': wwdr_certfile}

        if self.pass_signer.passphrase:
            args = '%s -passin pass:"%s"' % (args, self.pass_signer.passphrase)
        args = args.split()

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('openssl args: %s', " ".join(args))


        p = subprocess.Popen(" ".join(args), stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        signature = p.stdout.read()

        for f in (keyfile, certfile, wwdr_certfile, manifest_file):
            os.remove(f)

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug('signature length is  %d', len(signature))

        return signature

    def zip(self, manifest=None, signature=None):
        '''
        Zips up the pass in pkpass/zip format.
        '''
        s = StringIO()
        pkpass = zipfile.ZipFile(s, 'a')
        manifest = manifest or self.generate_manifest()
        pass_json = self.serialize()
        signature = signature or self.sign()
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
        return self.message


class Field(models.Model):
    _pass = models.ForeignKey(Pass, related_name='fields')
    key = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    value = models.TextField()

    FIELD_TYPES = (('header', 'header field'),
                   ('primary', 'primary field'),
                   ('secondary', 'secondary field'),
                   ('auxiliary', 'auxiliary field'),
                   ('back', 'back field'),)

    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    priority = models.PositiveSmallIntegerField('Field priority (0 is highest priority)', default=0)
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
    currency_code = models.CharField(max_length=5, null=True, blank=True)

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
        keys_and_attrs = (
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
        return u'key: %s, label: %s, value: %s' % (self.key, self.label, self.value[:20])

    class Meta:
        unique_together = ('_pass', 'key')  # Field keys need to be unique per pass


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


class Device(models.Model):
    push_token = models.CharField(max_length=255)
    device_library_id = models.CharField(max_length=255, unique=True)
    passes = models.ManyToManyField(Pass)
