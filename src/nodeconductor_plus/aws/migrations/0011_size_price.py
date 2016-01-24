# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0010_add_geoposition'),
    ]

    operations = [
        migrations.AddField(
            model_name='size',
            name='price',
            field=models.PositiveIntegerField(default=0, help_text=b'Hourly price in USD'),
            preserve_default=False,
        ),
    ]
