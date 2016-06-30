# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0017_volume'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='billing_backend_id',
            field=models.CharField(help_text='ID of a resource in backend', max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='instance',
            name='last_usage_update_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
