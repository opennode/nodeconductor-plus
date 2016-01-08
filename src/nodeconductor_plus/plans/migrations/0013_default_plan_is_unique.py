# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0012_update_plan_quota_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plan',
            name='is_default',
            field=models.BooleanField(default=False, unique=True),
            preserve_default=True,
        ),
    ]
