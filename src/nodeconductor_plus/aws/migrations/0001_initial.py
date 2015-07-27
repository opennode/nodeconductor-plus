# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm
import nodeconductor.structure.models
import django.db.models.deletion
import django.utils.timezone
import uuidfield.fields
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0016_init_nc_resource_count_quotas'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255, db_index=True)),
                ('settings', models.ForeignKey(related_name='+', blank=True, to='structure.ServiceSettings', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('description', models.CharField(max_length=500, verbose_name='description', blank=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('key_name', models.CharField(max_length=50, blank=True)),
                ('key_fingerprint', models.CharField(max_length=47, blank=True)),
                ('user_data', models.TextField(help_text='Additional data that will be added to instance on provisioning', blank=True, validators=[nodeconductor.structure.models.validate_yaml])),
                ('cores', models.PositiveSmallIntegerField(default=0, help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(default=0, help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(default=0, help_text='Disk size in MiB')),
                ('backend_id', models.CharField(max_length=255, blank=True)),
                ('start_time', models.DateTimeField(null=True, blank=True)),
                ('state', django_fsm.FSMIntegerField(default=1, help_text='WARNING! Should not be changed manually unless you really know what you are doing.', max_length=1, choices=[(1, 'Provisioning Scheduled'), (2, 'Provisioning'), (3, 'Online'), (4, 'Offline'), (5, 'Starting Scheduled'), (6, 'Starting'), (7, 'Stopping Scheduled'), (8, 'Stopping'), (9, 'Erred'), (10, 'Deletion Scheduled'), (11, 'Deleting'), (13, 'Resizing Scheduled'), (14, 'Resizing'), (15, 'Restarting Scheduled'), (16, 'Restarting')])),
                ('external_ips', models.GenericIPAddressField(null=True, protocol=b'IPv4', blank=True)),
                ('internal_ips', models.GenericIPAddressField(null=True, protocol=b'IPv4', blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('customer', models.ForeignKey(related_name='+', to='structure.Customer')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceProjectLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_fsm.FSMIntegerField(default=1, choices=[(1, 'Sync Scheduled'), (2, 'Syncing'), (3, 'In Sync'), (4, 'Erred')])),
                ('project', models.ForeignKey(related_name='+', to='structure.Project')),
                ('service', models.ForeignKey(to='aws.Service')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='service',
            name='projects',
            field=models.ManyToManyField(related_name='+', through='aws.ServiceProjectLink', to='structure.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='settings',
            field=models.ForeignKey(related_name='+', to='structure.ServiceSettings'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('customer', 'settings')]),
        ),
        migrations.AddField(
            model_name='instance',
            name='service_project_link',
            field=models.ForeignKey(related_name='instances', on_delete=django.db.models.deletion.PROTECT, to='aws.ServiceProjectLink'),
            preserve_default=True,
        ),
    ]
