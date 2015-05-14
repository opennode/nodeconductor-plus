# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_fsm
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0007_add_service_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='DigitalOceanProjectLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', django_fsm.FSMIntegerField(default=1, choices=[(1, 'Sync Scheduled'), (2, 'Syncing'), (3, 'In Sync'), (4, 'Erred')])),
                ('project', models.ForeignKey(to='structure.Project')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DigitalOceanService',
            fields=[
                ('service_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='structure.Service')),
                ('auth_token', models.CharField(max_length=64)),
                ('projects', models.ManyToManyField(related_name='services', through='digitalocean.DigitalOceanProjectLink', to='structure.Project')),
            ],
            options={
                'abstract': False,
            },
            bases=('structure.service',),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name')),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255)),
                ('service', models.ForeignKey(related_name='regions', to='digitalocean.DigitalOceanService')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='image',
            name='regions',
            field=models.ManyToManyField(to='digitalocean.Region'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='image',
            name='service',
            field=models.ForeignKey(related_name='images', to='digitalocean.DigitalOceanService'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='digitaloceanprojectlink',
            name='service',
            field=models.ForeignKey(to='digitalocean.DigitalOceanService'),
            preserve_default=True,
        ),
    ]
