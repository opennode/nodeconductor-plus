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
        ('gitlab', '0002_new_service_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='GitLabService',
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
            name='GitLabServiceProjectLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_fsm.FSMIntegerField(default=1, choices=[(1, 'Sync Scheduled'), (2, 'Syncing'), (3, 'In Sync'), (4, 'Erred')])),
                ('project', models.ForeignKey(to='structure.Project')),
                ('service', models.ForeignKey(to='gitlab.GitLabService')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='gitlabservice',
            name='projects',
            field=models.ManyToManyField(related_name='gitlab_services', through='gitlab.GitLabServiceProjectLink', to='structure.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='gitlabservice',
            name='settings',
            field=models.ForeignKey(to='structure.ServiceSettings'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='gitlabservice',
            unique_together=set([('customer', 'settings')]),
        ),
        migrations.RunSQL("INSERT INTO gitlab_gitlabservice SELECT * FROM gitlab_service"),
        migrations.RunSQL("INSERT INTO gitlab_gitlabserviceprojectlink SELECT * FROM gitlab_serviceprojectlink"),
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
            model_name='group',
            name='service_project_link',
            field=models.ForeignKey(related_name='groups', on_delete=django.db.models.deletion.PROTECT, to='gitlab.GitLabServiceProjectLink'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='service_project_link',
            field=models.ForeignKey(related_name='projects', on_delete=django.db.models.deletion.PROTECT, to='gitlab.GitLabServiceProjectLink'),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='ServiceProjectLink',
        ),
    ]
