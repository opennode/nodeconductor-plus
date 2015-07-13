# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import uuidfield.fields
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0014_servicesettings_options'),
        ('gitlab', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('customer', models.ForeignKey(related_name='+', to='structure.Customer')),
                ('settings', models.ForeignKey(related_name='+', to='structure.ServiceSettings')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RunSQL(
            "INSERT INTO gitlab_service (id, uuid, name, customer_id, settings_id) "
            "SELECT id, uuid, name, customer_id, settings_id "
            "FROM structure_service s JOIN gitlab_gitlabservice gs ON (s.id = gs.service_ptr_id);"
        ),
        migrations.CreateModel(
            name='ServiceProjectLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_fsm.FSMIntegerField(default=1, choices=[(1, 'Sync Scheduled'), (2, 'Syncing'), (3, 'In Sync'), (4, 'Erred')])),
                ('project', models.ForeignKey(related_name='+', to='structure.Project')),
                ('service', models.ForeignKey(to='gitlab.Service')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.RunSQL(
            "INSERT INTO gitlab_serviceprojectlink (id, state, project_id, service_id) "
            "SELECT id, state, project_id, service_id FROM gitlab_gitlabserviceprojectlink;"
        ),
        migrations.AddField(
            model_name='gitlabservice',
            name='tmp',
            field=models.CharField(max_length=10, blank=True),
        ),
        migrations.RemoveField(
            model_name='gitlabservice',
            name='projects',
        ),
        migrations.RemoveField(
            model_name='gitlabservice',
            name='service_ptr',
        ),
        migrations.RemoveField(
            model_name='gitlabserviceprojectlink',
            name='project',
        ),
        migrations.RemoveField(
            model_name='gitlabserviceprojectlink',
            name='service',
        ),
        migrations.DeleteModel(
            name='GitLabService',
        ),
        migrations.AddField(
            model_name='service',
            name='projects',
            field=models.ManyToManyField(related_name='+', through='gitlab.ServiceProjectLink', to='structure.Project'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='service',
            unique_together=set([('customer', 'settings')]),
        ),
        migrations.AlterField(
            model_name='group',
            name='service_project_link',
            field=models.ForeignKey(related_name='groups', on_delete=django.db.models.deletion.PROTECT, to='gitlab.ServiceProjectLink'),
            preserve_default=True,
        ),
        migrations.RunSQL("UPDATE gitlab_project SET web_url='' WHERE web_url is NULL"),
        migrations.RunSQL("UPDATE gitlab_project SET http_url_to_repo='' WHERE http_url_to_repo is NULL"),
        migrations.RunSQL("UPDATE gitlab_project SET ssh_url_to_repo='' WHERE ssh_url_to_repo is NULL"),
        migrations.AlterField(
            model_name='project',
            name='service_project_link',
            field=models.ForeignKey(related_name='projects', on_delete=django.db.models.deletion.PROTECT, to='gitlab.ServiceProjectLink'),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='GitLabServiceProjectLink',
        ),
    ]
