# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0002_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='plancustomer',
            name='uuid',
            field=uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True),
            preserve_default=True,
        ),
    ]
