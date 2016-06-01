# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0020_unique_spl'),
    ]

    operations = [
        migrations.AddField(
            model_name='droplet',
            name='min_disk',
            field=models.PositiveIntegerField(default=0, help_text='Minimum disk size in MiB'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='droplet',
            name='min_ram',
            field=models.PositiveIntegerField(default=0, help_text='Minimum memory size in MiB'),
            preserve_default=True,
        ),
    ]
