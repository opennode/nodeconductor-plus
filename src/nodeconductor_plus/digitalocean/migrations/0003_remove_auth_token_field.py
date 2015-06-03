# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0002_add_droplet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='digitaloceanservice',
            name='auth_token',
        ),
        migrations.AlterField(
            model_name='digitaloceanservice',
            name='projects',
            field=models.ManyToManyField(related_name='digitalocean_services', through='digitalocean.DigitalOceanServiceProjectLink', to='structure.Project'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='droplet',
            name='backend_id',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='droplet',
            name='service_project_link',
            field=models.ForeignKey(related_name='droplets', on_delete=django.db.models.deletion.PROTECT, to='digitalocean.DigitalOceanServiceProjectLink'),
            preserve_default=True,
        ),
    ]
