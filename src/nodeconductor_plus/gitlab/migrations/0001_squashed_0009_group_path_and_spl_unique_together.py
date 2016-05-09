# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_fsm
import django.utils.timezone
import django.db.models.deletion
import uuidfield.fields
import taggit.managers
import model_utils.fields
import nodeconductor.core.validators


class Migration(migrations.Migration):

    replaces = [(b'gitlab', '0001_initial'), (b'gitlab', '0002_new_service_model'), (b'gitlab', '0003_rename_service_models'), (b'gitlab', '0004_gitlabservice_available_for_all'), (b'gitlab', '0005_add_creation_states'), (b'gitlab', '0006_add_error_message'), (b'gitlab', '0007_resource_error_message'), (b'gitlab', '0008_add_tags'), (b'gitlab', '0009_group_path_and_spl_unique_together')]

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('structure', '0001_squashed_0021_balancehistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitLabService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('settings', models.ForeignKey(to='structure.ServiceSettings')),
                ('customer', models.ForeignKey(to='structure.Customer')),
                ('available_for_all', models.BooleanField(default=False, help_text='Service will be automatically added to all customers projects if it is available for all')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'GitLab service',
                'verbose_name_plural': 'GitLab services'
            },
        ),
        migrations.CreateModel(
            name='GitLabServiceProjectLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_fsm.FSMIntegerField(default=5, choices=[(0, 'New'), (5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Sync Scheduled'), (2, 'Syncing'), (3, 'In Sync'), (4, 'Erred')])),
                ('project', models.ForeignKey(to='structure.Project')),
                ('service', models.ForeignKey(to='gitlab.GitLabService')),
                ('error_message', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'GitLab service project link',
                'verbose_name_plural': 'GitLab service project links'
            },
        ),
        migrations.AlterUniqueTogether(
            name='gitlabservice',
            unique_together=set([('customer', 'settings')]),
        ),
        migrations.AddField(
            model_name='gitlabservice',
            name='projects',
            field=models.ManyToManyField(related_name='gitlab_services', through='gitlab.GitLabServiceProjectLink', to=b'structure.Project'),
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('description', models.CharField(max_length=500, verbose_name='description', blank=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('state', django_fsm.FSMIntegerField(default=1, help_text='WARNING! Should not be changed manually unless you really know what you are doing.', choices=[(1, 'Provisioning Scheduled'), (2, 'Provisioning'), (3, 'Online'), (4, 'Offline'), (5, 'Starting Scheduled'), (6, 'Starting'), (7, 'Stopping Scheduled'), (8, 'Stopping'), (9, 'Erred'), (10, 'Deletion Scheduled'), (11, 'Deleting'), (13, 'Resizing Scheduled'), (14, 'Resizing'), (15, 'Restarting Scheduled'), (16, 'Restarting')])),
                ('path', models.CharField(max_length=100, blank=True)),
                ('service_project_link', models.ForeignKey(related_name='groups', on_delete=django.db.models.deletion.PROTECT, to='gitlab.GitLabServiceProjectLink')),
                ('error_message', models.TextField(blank=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('description', models.CharField(max_length=500, verbose_name='description', blank=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('state', django_fsm.FSMIntegerField(default=1, help_text='WARNING! Should not be changed manually unless you really know what you are doing.', choices=[(1, 'Provisioning Scheduled'), (2, 'Provisioning'), (3, 'Online'), (4, 'Offline'), (5, 'Starting Scheduled'), (6, 'Starting'), (7, 'Stopping Scheduled'), (8, 'Stopping'), (9, 'Erred'), (10, 'Deletion Scheduled'), (11, 'Deleting'), (13, 'Resizing Scheduled'), (14, 'Resizing'), (15, 'Restarting Scheduled'), (16, 'Restarting')])),
                ('group', models.ForeignKey(related_name='projects', blank=True, to='gitlab.Group', null=True)),
                ('web_url', models.CharField(max_length=255, blank=True)),
                ('ssh_url_to_repo', models.CharField(max_length=255, blank=True)),
                ('http_url_to_repo', models.CharField(max_length=255, blank=True)),
                ('visibility_level', models.SmallIntegerField(choices=[(0, b'Project access must be granted explicitly for each user.'), (10, b'The project can be cloned by any logged in user.'), (20, b'The project can be cloned without any authentication.')])),
                ('service_project_link', models.ForeignKey(related_name='projects', on_delete=django.db.models.deletion.PROTECT, to='gitlab.GitLabServiceProjectLink')),
                ('error_message', models.TextField(blank=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=set([('path', 'service_project_link')]),
        ),
    ]
