# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'Field._pass'
        db.alter_column('passbook_field', '_pass_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['passbook.Pass']))

    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Field._pass'
        raise RuntimeError("Cannot reverse this migration. 'Field._pass' and its values cannot be restored.")

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
            'serial_number': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
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