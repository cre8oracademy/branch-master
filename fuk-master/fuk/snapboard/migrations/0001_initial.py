# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Category'
        db.create_table('snapboard_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('read_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sb_cat_read', to=orm['auth.Group'])),
            ('post_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sb_cat_post', to=orm['auth.Group'])),
            ('new_thread_group', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sb_cat_new_thread', to=orm['auth.Group'])),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50, db_index=True)),
        ))
        db.send_create_signal('snapboard', ['Category'])

        # Adding model 'Thread'
        db.create_table('snapboard_thread', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=255, db_index=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snapboard.Category'])),
            ('private', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('closed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sticky', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')()),
            ('updated', self.gf('django.db.models.fields.DateTimeField')()),
            ('last_poster', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sb_last_poster', null=True, to=orm['auth.User'])),
            ('post_count', self.gf('django.db.models.fields.IntegerField')(default=0, null=True)),
        ))
        db.send_create_signal('snapboard', ['Thread'])

        # Adding model 'Post'
        db.create_table('snapboard_post', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snapboard.Thread'])),
            ('text', self.gf('django.db.models.fields.TextField')()),
            ('status', self.gf('django.db.models.fields.CharField')(default='a', max_length=1)),
            ('date', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('edited', self.gf('django.db.models.fields.DateTimeField')(null=True)),
            ('ip', self.gf('django.db.models.fields.IPAddressField')(max_length=15, null=True, blank=True)),
        ))
        db.send_create_signal('snapboard', ['Post'])

        # Adding model 'Read'
        db.create_table('snapboard_read', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snapboard.Thread'])),
            ('time', self.gf('django.db.models.fields.DateTimeField')(blank=True)),
        ))
        db.send_create_signal('snapboard', ['Read'])

        # Adding unique constraint on 'Read', fields ['user', 'thread']
        db.create_unique('snapboard_read', ['user_id', 'thread_id'])

        # Adding model 'WatchList'
        db.create_table('snapboard_watchlist', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sb_watchlist', to=orm['auth.User'])),
            ('thread', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['snapboard.Thread'])),
        ))
        db.send_create_signal('snapboard', ['WatchList'])

        # Adding model 'NotifyRun'
        db.create_table('snapboard_notifyrun', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('starttime', self.gf('django.db.models.fields.DateTimeField')()),
            ('elapsed', self.gf('django.db.models.fields.IntegerField')()),
            ('threadcount', self.gf('django.db.models.fields.IntegerField')()),
            ('usercount', self.gf('django.db.models.fields.IntegerField')()),
            ('notifytype', self.gf('django.db.models.fields.CharField')(max_length=1)),
        ))
        db.send_create_signal('snapboard', ['NotifyRun'])

        # Adding model 'Moderation'
        db.create_table('snapboard_moderation', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('mod', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sb_moderator', to=orm['auth.User'])),
            ('oldstatus', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('newstatus', self.gf('django.db.models.fields.CharField')(max_length=1)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sb_mod_author', to=orm['auth.User'])),
            ('post', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sb_mod_post', to=orm['snapboard.Post'])),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('snapboard', ['Moderation'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Read', fields ['user', 'thread']
        db.delete_unique('snapboard_read', ['user_id', 'thread_id'])

        # Deleting model 'Category'
        db.delete_table('snapboard_category')

        # Deleting model 'Thread'
        db.delete_table('snapboard_thread')

        # Deleting model 'Post'
        db.delete_table('snapboard_post')

        # Deleting model 'Read'
        db.delete_table('snapboard_read')

        # Deleting model 'WatchList'
        db.delete_table('snapboard_watchlist')

        # Deleting model 'NotifyRun'
        db.delete_table('snapboard_notifyrun')

        # Deleting model 'Moderation'
        db.delete_table('snapboard_moderation')


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
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'})
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
            'date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'edited': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'a'", 'max_length': '1'}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['snapboard.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
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
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'db_index': 'True'}),
            'sticky': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'snapboard.watchlist': {
            'Meta': {'object_name': 'WatchList'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'thread': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['snapboard.Thread']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sb_watchlist'", 'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['snapboard']
