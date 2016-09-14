# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_fsm
import nodeconductor.structure.models
import django.utils.timezone
import django.db.models.deletion
import nodeconductor.core.fields
import taggit.managers
import model_utils.fields
import nodeconductor.core.validators


class Migration(migrations.Migration):

    replaces = [(b'digitalocean', '0001_initial'), (b'digitalocean', '0002_add_droplet'), (b'digitalocean', '0003_remove_auth_token_field'), (b'digitalocean', '0004_optional_service_property'), (b'digitalocean', '0005_image_type_and_distribution'), (b'digitalocean', '0006_droplet_ip_address'), (b'digitalocean', '0007_new_service_model'), (b'digitalocean', '0008_rename_service_models'), (b'digitalocean', '0009_digitaloceanservice_available_for_all'), (b'digitalocean', '0010_add_creation_states'), (b'digitalocean', '0011_unique_backend_id'), (b'digitalocean', '0012_add_error_message'), (b'digitalocean', '0013_resource_error_message'), (b'digitalocean', '0014_droplet_tags')]

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('structure', '0001_squashed_0021_balancehistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='DigitalOceanService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('settings', models.ForeignKey(to='structure.ServiceSettings')),
                ('customer', models.ForeignKey(to='structure.Customer')),
                ('available_for_all', models.BooleanField(default=False, help_text='Service will be automatically added to all customers projects if it is available for all')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'DigitalOcean service',
                'verbose_name_plural': 'DigitalOcean services'
            },
        ),
        migrations.CreateModel(
            name='DigitalOceanServiceProjectLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_fsm.FSMIntegerField(default=5, choices=[(0, 'New'), (5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Sync Scheduled'), (2, 'Syncing'), (3, 'In Sync'), (4, 'Erred')])),
                ('project', models.ForeignKey(to='structure.Project')),
                ('service', models.ForeignKey(to='digitalocean.DigitalOceanService')),
                ('error_message', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'DigitalOcean service project link',
                'verbose_name_plural': 'DigitalOcean service project links'
            },
        ),
        migrations.AlterUniqueTogether(
            name='digitaloceanservice',
            unique_together=set([('customer', 'settings')]),
        ),
        migrations.AddField(
            model_name='digitaloceanservice',
            name='projects',
            field=models.ManyToManyField(related_name='digitalocean_services', through='digitalocean.DigitalOceanServiceProjectLink', to=b'structure.Project'),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('backend_id', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('backend_id', models.CharField(unique=True, max_length=255)),
                ('regions', models.ManyToManyField(to=b'digitalocean.Region')),
                ('type', models.CharField(max_length=100)),
                ('distribution', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('backend_id', models.CharField(unique=True, max_length=255)),
                ('cores', models.PositiveSmallIntegerField(help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(help_text='Disk size in MiB')),
                ('transfer', models.PositiveIntegerField(help_text='Amount of transfer bandwidth in MiB')),
                ('regions', models.ManyToManyField(to=b'digitalocean.Region')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Droplet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=500, verbose_name='description', blank=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('backend_id', models.CharField(max_length=255, blank=True)),
                ('key_name', models.CharField(max_length=50, blank=True)),
                ('key_fingerprint', models.CharField(max_length=47, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('user_data', models.TextField(help_text='Additional data that will be added to instance on provisioning', blank=True, validators=[nodeconductor.structure.models.validate_yaml])),
                ('state', django_fsm.FSMIntegerField(default=1, help_text='WARNING! Should not be changed manually unless you really know what you are doing.', choices=[(1, 'Provisioning Scheduled'), (2, 'Provisioning'), (3, 'Online'), (4, 'Offline'), (5, 'Starting Scheduled'), (6, 'Starting'), (7, 'Stopping Scheduled'), (8, 'Stopping'), (9, 'Erred'), (10, 'Deletion Scheduled'), (11, 'Deleting'), (13, 'Resizing Scheduled'), (14, 'Resizing'), (15, 'Restarting Scheduled'), (16, 'Restarting')])),
                ('cores', models.PositiveSmallIntegerField(default=0, help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(default=0, help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(default=0, help_text='Disk size in MiB')),
                ('transfer', models.PositiveIntegerField(default=0, help_text='Amount of transfer bandwidth in MiB')),
                ('service_project_link', models.ForeignKey(related_name='droplets', on_delete=django.db.models.deletion.PROTECT, to='digitalocean.DigitalOceanServiceProjectLink')),
                ('ip_address', models.GenericIPAddressField(null=True, protocol='IPv4', blank=True)),
                ('error_message', models.TextField(blank=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
