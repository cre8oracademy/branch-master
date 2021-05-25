# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'GitAction'
        db.create_table('git_posthook_gitaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('payload', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('result', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('git_posthook', ['GitAction'])


    def backwards(self, orm):
        
        # Deleting model 'GitAction'
        db.delete_table('git_posthook_gitaction')


    models = {
        'git_posthook.gitaction': {
            'Meta': {'object_name': 'GitAction'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payload': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'result': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        }
    }

    complete_apps = ['git_posthook']
