# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm
import django.utils.timezone
import django.db.models.deletion
import uuidfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0013_servicesettings_customer'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitLabService',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='structure.Service')),
            ],
            options={
                'abstract': False,
            },
            bases=('structure.service',),
        ),
        migrations.CreateModel(
            name='GitLabServiceProjectLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_fsm.FSMIntegerField(default=1, choices=[(1, 'Sync Scheduled'), (2, 'Syncing'), (3, 'In Sync'), (4, 'Erred')])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('description', models.CharField(max_length=500, verbose_name='description', blank=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('state', django_fsm.FSMIntegerField(default=1, help_text='WARNING! Should not be changed manually unless you really know what you are doing.', max_length=1, choices=[(1, 'Provisioning Scheduled'), (2, 'Provisioning'), (3, 'Online'), (4, 'Offline'), (5, 'Starting Scheduled'), (6, 'Starting'), (7, 'Stopping Scheduled'), (8, 'Stopping'), (9, 'Erred'), (10, 'Deletion Scheduled'), (11, 'Deleting'), (13, 'Resizing Scheduled'), (14, 'Resizing'), (15, 'Restarting Scheduled'), (16, 'Restarting')])),
                ('path', models.CharField(max_length=100, blank=True)),
                ('service_project_link', models.ForeignKey(related_name='groups', on_delete=django.db.models.deletion.PROTECT, to='gitlab.GitLabServiceProjectLink')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('description', models.CharField(max_length=500, verbose_name='description', blank=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('state', django_fsm.FSMIntegerField(default=1, help_text='WARNING! Should not be changed manually unless you really know what you are doing.', max_length=1, choices=[(1, 'Provisioning Scheduled'), (2, 'Provisioning'), (3, 'Online'), (4, 'Offline'), (5, 'Starting Scheduled'), (6, 'Starting'), (7, 'Stopping Scheduled'), (8, 'Stopping'), (9, 'Erred'), (10, 'Deletion Scheduled'), (11, 'Deleting'), (13, 'Resizing Scheduled'), (14, 'Resizing'), (15, 'Restarting Scheduled'), (16, 'Restarting')])),
                ('group', models.ForeignKey(related_name='projects', blank=True, to='gitlab.Group', null=True)),
                ('web_url', models.CharField(max_length=255, blank=True)),
                ('ssh_url_to_repo', models.CharField(max_length=255, blank=True)),
                ('http_url_to_repo', models.CharField(max_length=255, blank=True)),
                ('visibility_level', models.SmallIntegerField(choices=[(0, b'Project access must be granted explicitly for each user.'), (10, b'The project can be cloned by any logged in user.'), (20, b'The project can be cloned without any authentication.')])),
                ('service_project_link', models.ForeignKey(related_name='projects', on_delete=django.db.models.deletion.PROTECT, to='gitlab.GitLabServiceProjectLink')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='gitlabserviceprojectlink',
            name='project',
            field=models.ForeignKey(to='structure.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitlabserviceprojectlink',
            name='service',
            field=models.ForeignKey(to='gitlab.GitLabService'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitlabservice',
            name='projects',
            field=models.ManyToManyField(related_name='gitlab_services', through='gitlab.GitLabServiceProjectLink', to='structure.Project'),
            preserve_default=True,
        ),
    ]
