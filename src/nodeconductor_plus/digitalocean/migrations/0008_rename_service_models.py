# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import uuidfield.fields
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0016_init_nc_resource_count_quotas'),
        ('digitalocean', '0007_new_service_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='DigitalOceanService',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('customer', models.ForeignKey(to='structure.Customer')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DigitalOceanServiceProjectLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_fsm.FSMIntegerField(default=1, choices=[(1, 'Sync Scheduled'), (2, 'Syncing'), (3, 'In Sync'), (4, 'Erred')])),
                ('project', models.ForeignKey(to='structure.Project')),
                ('service', models.ForeignKey(to='digitalocean.DigitalOceanService')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='digitaloceanservice',
            name='projects',
            field=models.ManyToManyField(related_name='digitalocean_services', through='digitalocean.DigitalOceanServiceProjectLink', to='structure.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='digitaloceanservice',
            name='settings',
            field=models.ForeignKey(to='structure.ServiceSettings'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='digitaloceanservice',
            unique_together=set([('customer', 'settings')]),
        ),
        migrations.RunSQL("INSERT INTO digitalocean_digitaloceanservice SELECT * FROM digitalocean_service"),
        migrations.RunSQL("INSERT INTO digitalocean_digitaloceanserviceprojectlink SELECT * FROM digitalocean_serviceprojectlink"),
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
            model_name='droplet',
            name='service_project_link',
            field=models.ForeignKey(related_name='droplets', on_delete=django.db.models.deletion.PROTECT, to='digitalocean.DigitalOceanServiceProjectLink'),
            preserve_default=True,
        ),
        migrations.DeleteModel(
            name='ServiceProjectLink',
        ),
    ]
