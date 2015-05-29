# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodeconductor.iaas.models
import django.utils.timezone
import model_utils.fields
import django.db.models.deletion
import django_fsm
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0009_update_service_models'),
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
                ('backend_id', models.CharField(max_length=255, db_index=True)),
                ('key_name', models.CharField(max_length=50, blank=True)),
                ('key_fingerprint', models.CharField(max_length=47, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('user_data', models.TextField(help_text='Additional data that will be added to instance on provisioning', blank=True, validators=[nodeconductor.iaas.models.validate_yaml])),
                ('state', django_fsm.FSMIntegerField(default=1, help_text='WARNING! Should not be changed manually unless you really know what you are doing.', max_length=1, choices=[(1, 'Provisioning Scheduled'), (2, 'Provisioning'), (3, 'Online'), (4, 'Offline'), (5, 'Starting Scheduled'), (6, 'Starting'), (7, 'Stopping Scheduled'), (8, 'Stopping'), (9, 'Erred'), (10, 'Deletion Scheduled'), (11, 'Deleting'), (13, 'Resizing Scheduled'), (14, 'Resizing'), (15, 'Restarting Scheduled'), (16, 'Restarting')])),
                ('cores', models.PositiveSmallIntegerField(default=0, help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(default=0, help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(default=0, help_text='Disk size in MiB')),
                ('transfer', models.PositiveIntegerField(default=0, help_text='Amount of transfer bandwidth in MiB')),
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
                ('backend_id', models.CharField(max_length=255, db_index=True)),
                ('cores', models.PositiveSmallIntegerField(help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(help_text='Disk size in MiB')),
                ('transfer', models.PositiveIntegerField(help_text='Amount of transfer bandwidth in MiB')),
                ('regions', models.ManyToManyField(to='digitalocean.Region')),
                ('settings', models.ForeignKey(related_name='+', to='structure.ServiceSettings')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='image',
            name='service',
        ),
        migrations.RemoveField(
            model_name='region',
            name='service',
        ),
        migrations.AddField(
            model_name='image',
            name='settings',
            field=models.ForeignKey(related_name='+', to='structure.ServiceSettings'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='region',
            name='settings',
            field=models.ForeignKey(related_name='+', to='structure.ServiceSettings'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='image',
            name='backend_id',
            field=models.CharField(max_length=255, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='region',
            name='backend_id',
            field=models.CharField(max_length=255, db_index=True),
            preserve_default=True,
        ),
    ]
