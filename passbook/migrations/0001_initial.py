# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Signer'
        db.create_table('passbook_signer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('label', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('certificate', self.gf('django.db.models.fields.TextField')()),
            ('private_key', self.gf('django.db.models.fields.TextField')()),
            ('wwdr_certificate', self.gf('django.db.models.fields.TextField')()),
            ('passphrase', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
        ))
        db.send_create_signal('passbook', ['Signer'])

        # Adding model 'Pass'
        db.create_table('passbook_pass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('identifier', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('serial_number', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('organization_name', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('team_identifier', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.CharField')(default='', max_length=255, null=True, blank=True)),
            ('auth_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('relevant_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('barcode', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='passes', null=True, to=orm['passbook.Barcode'])),
            ('background_color', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('foreground_color', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('label_color', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('logo', self.gf('django.db.models.fields.FilePathField')(recursive=True, max_length=100, blank=True, path='/Users/tim/WorkCode/passbook_service/opass/media/passbook', null=True, match='.*\\.(png|PNG)$')),
            ('icon', self.gf('django.db.models.fields.FilePathField')(path='/Users/tim/WorkCode/passbook_service/opass/media/passbook', max_length=100, recursive=True, match='.*\\.(png|PNG)$')),
            ('thumbnail_image', self.gf('django.db.models.fields.FilePathField')(recursive=True, max_length=100, blank=True, path='/Users/tim/WorkCode/passbook_service/opass/media/passbook', null=True, match='.*\\.(png|PNG)$')),
            ('background_image', self.gf('django.db.models.fields.FilePathField')(recursive=True, max_length=100, blank=True, path='/Users/tim/WorkCode/passbook_service/opass/media/passbook', null=True, match='.*\\.(png|PNG)$')),
            ('strip_image', self.gf('django.db.models.fields.FilePathField')(recursive=True, max_length=100, blank=True, path='/Users/tim/WorkCode/passbook_service/opass/media/passbook', null=True, match='.*\\.(png|PNG)$')),
            ('supress_strip_shine', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('logo_text', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('enable_web_service', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('pass_signer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['passbook.Signer'])),
            ('transit_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('created_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('updated_at', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('passbook', ['Pass'])

        # Adding M2M table for field locations on 'Pass'
        db.create_table('passbook_pass_locations', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('pass', models.ForeignKey(orm['passbook.pass'], null=False)),
            ('location', models.ForeignKey(orm['passbook.location'], null=False))
        ))
        db.create_unique('passbook_pass_locations', ['pass_id', 'location_id'])

        # Adding model 'Barcode'
        db.create_table('passbook_barcode', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('message', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('format', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('encoding', self.gf('django.db.models.fields.CharField')(default='iso-8859-1', max_length=50)),
            ('alt_text', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('passbook', ['Barcode'])

        # Adding model 'Field'
        db.create_table('passbook_field', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('_pass', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='fields', null=True, to=orm['passbook.Pass'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('label', self.gf('django.db.models.fields.CharField')(default='', max_length=255, blank=True)),
            ('value', self.gf('django.db.models.fields.TextField')()),
            ('field_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('priority', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('text_alignment', self.gf('django.db.models.fields.CharField')(max_length=22, null=True, blank=True)),
            ('change_message', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('date_style', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('time_style', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('is_relative', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
            ('currency_code', self.gf('django.db.models.fields.CharField')(max_length=5, null=True, blank=True)),
            ('number_style', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
        ))
        db.send_create_signal('passbook', ['Field'])

        # Adding unique constraint on 'Field', fields ['_pass', 'key']
        db.create_unique('passbook_field', ['_pass_id', 'key'])

        # Adding model 'Location'
        db.create_table('passbook_location', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('longitude', self.gf('django.db.models.fields.FloatField')()),
            ('latitude', self.gf('django.db.models.fields.FloatField')()),
            ('altitude', self.gf('django.db.models.fields.FloatField')(null=True)),
            ('relevant_text', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('key', self.gf('django.db.models.fields.CharField')(default='empty', max_length=255)),
        ))
        db.send_create_signal('passbook', ['Location'])

        # Adding model 'Device'
        db.create_table('passbook_device', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('push_token', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('device_library_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
        ))
        db.send_create_signal('passbook', ['Device'])

        # Adding M2M table for field passes on 'Device'
        db.create_table('passbook_device_passes', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('device', models.ForeignKey(orm['passbook.device'], null=False)),
            ('pass', models.ForeignKey(orm['passbook.pass'], null=False))
        ))
        db.create_unique('passbook_device_passes', ['device_id', 'pass_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Field', fields ['_pass', 'key']
        db.delete_unique('passbook_field', ['_pass_id', 'key'])

        # Deleting model 'Signer'
        db.delete_table('passbook_signer')

        # Deleting model 'Pass'
        db.delete_table('passbook_pass')

        # Removing M2M table for field locations on 'Pass'
        db.delete_table('passbook_pass_locations')

        # Deleting model 'Barcode'
        db.delete_table('passbook_barcode')

        # Deleting model 'Field'
        db.delete_table('passbook_field')

        # Deleting model 'Location'
        db.delete_table('passbook_location')

        # Deleting model 'Device'
        db.delete_table('passbook_device')

        # Removing M2M table for field passes on 'Device'
        db.delete_table('passbook_device_passes')


    models = {
        'passbook.barcode': {
            'Meta': {'object_name': 'Barcode'},
            'alt_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'encoding': ('django.db.models.fields.CharField', [], {'default': "'iso-8859-1'", 'max_length': '50'}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'passbook.device': {
            'Meta': {'object_name': 'Device'},
            'device_library_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'passes': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['passbook.Pass']", 'symmetrical': 'False'}),
            'push_token': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'passbook.field': {
            'Meta': {'unique_together': "(('_pass', 'key'),)", 'object_name': 'Field'},
            '_pass': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fields'", 'null': 'True', 'to': "orm['passbook.Pass']"}),
            'change_message': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'currency_code': ('django.db.models.fields.CharField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'date_style': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'field_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_relative': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'label': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'number_style': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'priority': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'text_alignment': ('django.db.models.fields.CharField', [], {'max_length': '22', 'null': 'True', 'blank': 'True'}),
            'time_style': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'passbook.location': {
            'Meta': {'object_name': 'Location'},
            'altitude': ('django.db.models.fields.FloatField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'default': "'empty'", 'max_length': '255'}),
            'latitude': ('django.db.models.fields.FloatField', [], {}),
            'longitude': ('django.db.models.fields.FloatField', [], {}),
            'relevant_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'passbook.pass': {
            'Meta': {'object_name': 'Pass'},
            'auth_token': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'background_color': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'background_image': ('django.db.models.fields.FilePathField', [], {'recursive': 'True', 'max_length': '100', 'blank': 'True', 'path': "'/Users/tim/WorkCode/passbook_service/opass/media/passbook'", 'null': 'True', 'match': "'.*\\\\.(png|PNG)$'"}),
            'barcode': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'passes'", 'null': 'True', 'to': "orm['passbook.Barcode']"}),
            'created_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'enable_web_service': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'foreground_color': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'icon': ('django.db.models.fields.FilePathField', [], {'path': "'/Users/tim/WorkCode/passbook_service/opass/media/passbook'", 'max_length': '100', 'recursive': 'True', 'match': "'.*\\\\.(png|PNG)$'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'label_color': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'locations': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'passes'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['passbook.Location']"}),
            'logo': ('django.db.models.fields.FilePathField', [], {'recursive': 'True', 'max_length': '100', 'blank': 'True', 'path': "'/Users/tim/WorkCode/passbook_service/opass/media/passbook'", 'null': 'True', 'match': "'.*\\\\.(png|PNG)$'"}),
            'logo_text': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'organization_name': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'pass_signer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['passbook.Signer']"}),
            'relevant_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'serial_number': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'strip_image': ('django.db.models.fields.FilePathField', [], {'recursive': 'True', 'max_length': '100', 'blank': 'True', 'path': "'/Users/tim/WorkCode/passbook_service/opass/media/passbook'", 'null': 'True', 'match': "'.*\\\\.(png|PNG)$'"}),
            'supress_strip_shine': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'team_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'thumbnail_image': ('django.db.models.fields.FilePathField', [], {'recursive': 'True', 'max_length': '100', 'blank': 'True', 'path': "'/Users/tim/WorkCode/passbook_service/opass/media/passbook'", 'null': 'True', 'match': "'.*\\\\.(png|PNG)$'"}),
            'transit_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'passbook.signer': {
            'Meta': {'object_name': 'Signer'},
            'certificate': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'label': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'passphrase': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'private_key': ('django.db.models.fields.TextField', [], {}),
            'wwdr_certificate': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['passbook']