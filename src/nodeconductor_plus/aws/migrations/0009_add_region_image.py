# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields

import nodeconductor.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0008_instance_tags'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(unique=True, max_length=255)),
            ],
            options={
                'abstract': False,
                'ordering': ['name']
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name])),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(unique=True, max_length=255)),
                ('cores', models.PositiveSmallIntegerField(help_text=b'Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(help_text=b'Memory size in MiB')),
                ('disk', models.PositiveIntegerField(help_text=b'Disk size in MiB')),
                ('regions', models.ManyToManyField(to='aws.Region')),
            ],
            options={
                'abstract': False,
                'ordering': ['cores', 'ram']
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='image',
            name='region',
            field=models.ForeignKey(default=1, to='aws.Region'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='instance',
            name='region',
            field=models.ForeignKey(default=1, to='aws.Region'),
            preserve_default=False,
        ),
    ]
