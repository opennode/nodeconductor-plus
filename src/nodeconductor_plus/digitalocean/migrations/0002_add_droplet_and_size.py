# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import model_utils.fields
import django.db.models.deletion
import django_fsm
import uuidfield.fields
import nodeconductor.structure.models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Droplet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=500, verbose_name='description', blank=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('cores', models.PositiveSmallIntegerField(blank=True, null=True, help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(blank=True, null=True, help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(blank=True, null=True, help_text='Disk size in MiB')),
                ('bandwidth', models.PositiveIntegerField(blank=True, null=True, help_text='Bandwidth size in MiB')),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('user_data', models.TextField(help_text='Additional data that will be added to resource on provisioning', blank=True, validators=[nodeconductor.structure.models.validate_yaml])),
                ('state', django_fsm.FSMIntegerField(default=1, help_text='WARNING! Should not be changed manually unless you really know what you are doing.', max_length=1, choices=[(1, 'Provisioning Scheduled'), (2, 'Provisioning'), (3, 'Online'), (4, 'Offline'), (5, 'Starting Scheduled'), (6, 'Starting'), (7, 'Stopping Scheduled'), (8, 'Stopping'), (9, 'Erred'), (10, 'Deletion Scheduled'), (11, 'Deleting'), (13, 'Resizing Scheduled'), (14, 'Resizing'), (15, 'Restarting Scheduled'), (16, 'Restarting')])),
                ('service_project_link', models.ForeignKey(related_name='resources', on_delete=django.db.models.deletion.PROTECT, to='digitalocean.DigitalOceanServiceProjectLink')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255)),
                ('cores', models.PositiveSmallIntegerField(help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(help_text='Disk size in MiB')),
                ('bandwidth', models.PositiveIntegerField(help_text='Bandwidth size in MiB')),
                ('regions', models.ManyToManyField(to='digitalocean.Region')),
                ('service', models.ForeignKey(related_name='sizes', to='digitalocean.DigitalOceanService')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
