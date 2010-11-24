# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'SocialProfile'
        db.create_table('socialregistration_socialprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='social', to=orm['auth.User'])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'])),
        ))
        db.send_create_signal('socialregistration', ['SocialProfile'])

        # Adding model 'FacebookProfile'
        db.create_table('socialregistration_facebookprofile', (
            ('socialprofile_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['socialregistration.SocialProfile'], unique=True, primary_key=True)),
            ('uid', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('access_token', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('socialregistration', ['FacebookProfile'])

        # Adding model 'TwitterProfile'
        db.create_table('socialregistration_twitterprofile', (
            ('socialprofile_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['socialregistration.SocialProfile'], unique=True, primary_key=True)),
            ('twitter_id', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('socialregistration', ['TwitterProfile'])

        # Adding model 'HyvesProfile'
        db.create_table('socialregistration_hyvesprofile', (
            ('socialprofile_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['socialregistration.SocialProfile'], unique=True, primary_key=True)),
            ('hyves_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('avatar', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('socialregistration', ['HyvesProfile'])

        # Adding model 'LinkedinProfile'
        db.create_table('socialregistration_linkedinprofile', (
            ('socialprofile_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['socialregistration.SocialProfile'], unique=True, primary_key=True)),
            ('linkedin_id', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('socialregistration', ['LinkedinProfile'])

        # Adding model 'FriendFeedProfile'
        db.create_table('socialregistration_friendfeedprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
        ))
        db.send_create_signal('socialregistration', ['FriendFeedProfile'])

        # Adding model 'OpenIDProfile'
        db.create_table('socialregistration_openidprofile', (
            ('socialprofile_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['socialregistration.SocialProfile'], unique=True, primary_key=True)),
            ('identity', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('socialregistration', ['OpenIDProfile'])

        # Adding model 'OpenIDStore'
        db.create_table('socialregistration_openidstore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('server_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('handle', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('secret', self.gf('django.db.models.fields.TextField')()),
            ('issued', self.gf('django.db.models.fields.IntegerField')()),
            ('lifetime', self.gf('django.db.models.fields.IntegerField')()),
            ('assoc_type', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal('socialregistration', ['OpenIDStore'])

        # Adding model 'OpenIDNonce'
        db.create_table('socialregistration_openidnonce', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('server_url', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('timestamp', self.gf('django.db.models.fields.IntegerField')()),
            ('salt', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('socialregistration', ['OpenIDNonce'])


    def backwards(self, orm):
        
        # Deleting model 'SocialProfile'
        db.delete_table('socialregistration_socialprofile')

        # Deleting model 'FacebookProfile'
        db.delete_table('socialregistration_facebookprofile')

        # Deleting model 'TwitterProfile'
        db.delete_table('socialregistration_twitterprofile')

        # Deleting model 'HyvesProfile'
        db.delete_table('socialregistration_hyvesprofile')

        # Deleting model 'LinkedinProfile'
        db.delete_table('socialregistration_linkedinprofile')

        # Deleting model 'FriendFeedProfile'
        db.delete_table('socialregistration_friendfeedprofile')

        # Deleting model 'OpenIDProfile'
        db.delete_table('socialregistration_openidprofile')

        # Deleting model 'OpenIDStore'
        db.delete_table('socialregistration_openidstore')

        # Deleting model 'OpenIDNonce'
        db.delete_table('socialregistration_openidnonce')


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
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'socialregistration.facebookprofile': {
            'Meta': {'object_name': 'FacebookProfile', '_ormbases': ['socialregistration.SocialProfile']},
            'access_token': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'socialprofile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['socialregistration.SocialProfile']", 'unique': 'True', 'primary_key': 'True'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'socialregistration.friendfeedprofile': {
            'Meta': {'object_name': 'FriendFeedProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'socialregistration.hyvesprofile': {
            'Meta': {'object_name': 'HyvesProfile', '_ormbases': ['socialregistration.SocialProfile']},
            'avatar': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'}),
            'hyves_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'socialprofile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['socialregistration.SocialProfile']", 'unique': 'True', 'primary_key': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '255', 'blank': 'True'})
        },
        'socialregistration.linkedinprofile': {
            'Meta': {'object_name': 'LinkedinProfile', '_ormbases': ['socialregistration.SocialProfile']},
            'linkedin_id': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'socialprofile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['socialregistration.SocialProfile']", 'unique': 'True', 'primary_key': 'True'})
        },
        'socialregistration.openidnonce': {
            'Meta': {'object_name': 'OpenIDNonce'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'salt': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'server_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {})
        },
        'socialregistration.openidprofile': {
            'Meta': {'object_name': 'OpenIDProfile', '_ormbases': ['socialregistration.SocialProfile']},
            'identity': ('django.db.models.fields.TextField', [], {}),
            'socialprofile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['socialregistration.SocialProfile']", 'unique': 'True', 'primary_key': 'True'})
        },
        'socialregistration.openidstore': {
            'Meta': {'object_name': 'OpenIDStore'},
            'assoc_type': ('django.db.models.fields.TextField', [], {}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'issued': ('django.db.models.fields.IntegerField', [], {}),
            'lifetime': ('django.db.models.fields.IntegerField', [], {}),
            'secret': ('django.db.models.fields.TextField', [], {}),
            'server_url': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"})
        },
        'socialregistration.socialprofile': {
            'Meta': {'object_name': 'SocialProfile'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'social'", 'to': "orm['auth.User']"}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'socialregistration.twitterprofile': {
            'Meta': {'object_name': 'TwitterProfile', '_ormbases': ['socialregistration.SocialProfile']},
            'socialprofile_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['socialregistration.SocialProfile']", 'unique': 'True', 'primary_key': 'True'}),
            'twitter_id': ('django.db.models.fields.PositiveIntegerField', [], {})
        }
    }

    complete_apps = ['socialregistration']
