# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0009_add_region_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='latitude',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='instance',
            name='longitude',
            field=models.FloatField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
