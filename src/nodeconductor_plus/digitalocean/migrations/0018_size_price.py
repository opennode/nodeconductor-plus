# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0017_add_geoposition'),
    ]

    operations = [
        migrations.AddField(
            model_name='size',
            name='price',
            field=models.PositiveIntegerField(default=0, help_text='Hourly price in USD'),
            preserve_default=False,
        ),
    ]
