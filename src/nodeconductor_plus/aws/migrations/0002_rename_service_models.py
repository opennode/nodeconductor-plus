# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import uuidfield.fields
import django_fsm

import nodeconductor.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0016_init_nc_resource_count_quotas'),
        ('aws', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AWSService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('customer', models.ForeignKey(to='structure.Customer')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AWSServiceProjectLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_fsm.FSMIntegerField(default=1, choices=[(1, 'Sync Scheduled'), (2, 'Syncing'), (3, 'In Sync'), (4, 'Erred')])),
                ('project', models.ForeignKey(to='structure.Project')),
                ('service', models.ForeignKey(to='aws.AWSService')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='awsservice',
            name='projects',
            field=models.ManyToManyField(related_name='aws_services', through='aws.AWSServiceProjectLink', to='structure.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='awsservice',
            name='settings',
            field=models.ForeignKey(to='structure.ServiceSettings'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='awsservice',
            unique_together=set([('customer', 'settings')]),
        ),
        migrations.RunSQL("INSERT INTO aws_awsservice SELECT * FROM aws_service"),
        migrations.RunSQL("INSERT INTO aws_awsserviceprojectlink SELECT * FROM aws_serviceprojectlink"),
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='service',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='service',
            name='projects',
        ),
        migrations.RemoveField(
            model_name='service',
            name='settings',
        ),
        migrations.RemoveField(
            model_name='serviceprojectlink',
            name='project',
        ),
        migrations.RemoveField(
            model_name='serviceprojectlink',
            name='service',
        ),
        migrations.DeleteModel(
            name='Service',
        ),
        migrations.AlterField(
            model_name='instance',
            name='service_project_link',
            field=models.ForeignKey(related_name='instances', on_delete=django.db.models.deletion.PROTECT, to='aws.AWSServiceProjectLink'),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='ServiceProjectLink',
        ),
    ]
