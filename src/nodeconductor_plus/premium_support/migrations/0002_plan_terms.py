# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('premium_support', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='terms',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
