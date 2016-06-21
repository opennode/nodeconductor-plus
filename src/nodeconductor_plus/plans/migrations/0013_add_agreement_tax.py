# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0012_update_plan_quota_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='plan',
            name='backend_id',
        ),
        migrations.AddField(
            model_name='agreement',
            name='tax',
            field=models.DecimalField(default=0, max_digits=9, decimal_places=2),
        ),
    ]
