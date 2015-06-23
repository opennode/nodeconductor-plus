# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0004_optional_service_property'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='distribution',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='image',
            name='type',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
    ]
