# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding index on 'Post', fields ['status']
        db.create_index('snapboard_post', ['status'])


        # Changing field 'Post.user'
        db.alter_column('snapboard_post', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL))
        # Adding index on 'Post', fields ['date']
        db.create_index('snapboard_post', ['date'])

        # Adding field 'Thread.show_og'
        db.add_column('snapboard_thread', 'show_og',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


        # Changing field 'Thread.user'
        db.alter_column('snapboard_thread', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True, on_delete=models.SET_NULL))

    def backwards(self, orm):
        # Removing index on 'Post', fields ['date']
        db.delete_index('snapboard_post', ['date'])

        # Removing index on 'Post', fields ['status']
        db.delete_index('snapboard_post', ['status'])


        # Changing field 'Post.user'
        db.alter_column('snapboard_post', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))
        # Deleting field 'Thread.show_og'
        db.delete_column('snapboard_thread', 'show_og')


        # Changing field 'Thread.user'
        db.alter_column('snapboard_thread', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'], null=True))

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'snapboard.category': {
            'Meta': {'object_name': 'Category'},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'new_thread_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sb_cat_new_thread'", 'to': "orm['auth.Group']"}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'post_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sb_cat_post'", 'to': "orm['auth.Group']"}),
            'read_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sb_cat_read'", 'to': "orm['auth.Group']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'})
        },
        'snapboard.moderation': {
            'Meta': {'object_name': 'Moderation'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sb_mod_author'", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mod': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sb_moderator'", 'to': "orm['auth.User']"}),
            'newstatus': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'oldstatus': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sb_mod_post'", 'to': "orm['snapboard.Post']"}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'snapboard.notifyrun': {
            'Meta': {'object_name': 'NotifyRun'},
            'elapsed': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notifytype': ('django.db.models.fields.CharField', [], {'max_length': '1'}),
            'starttime': ('django.db.models.fields.DateTimeField', [], {}),
            'threadcount': ('django.db.models.fields.IntegerField', [], {}),
            'usercount': ('django.db.models.fields.IntegerField', [], {})
        },
        'snapboard.post': {
            'Meta': {'ordering': "['date']", 'object_name': 'Post'},
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'db_index': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'a'", 'max_length': '1', 'db_index': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['snapboard.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        'snapboard.read': {
            'Meta': {'unique_together': "[('user', 'thread')]", 'object_name': 'Read'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['snapboard.Thread']"}),
            'time': ('django.db.models.fields.DateTimeField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'snapboard.thread': {
            'Meta': {'object_name': 'Thread'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['snapboard.Category']"}),
            'closed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'created': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_poster': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sb_last_poster'", 'null': 'True', 'to': "orm['auth.User']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'post_count': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True'}),
            'private': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'show_og': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255'}),
            'sticky': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']", 'null': 'True', 'on_delete': 'models.SET_NULL'})
        },
        'snapboard.watchlist': {
            'Meta': {'object_name': 'WatchList'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['snapboard.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sb_watchlist'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['snapboard']