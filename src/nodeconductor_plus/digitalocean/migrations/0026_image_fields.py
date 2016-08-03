# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0025_droplet_paid_resource'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='is_official',
            field=models.BooleanField(default=False, help_text='Is image provided by DigitalOcean'),
        ),
        migrations.AddField(
            model_name='image',
            name='created_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='min_disk_size',
            field=models.PositiveIntegerField(help_text='Minimum disk required for a size to use this image', null=True),
        ),
    ]
