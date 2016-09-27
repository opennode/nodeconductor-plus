# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0026_image_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='droplet',
            name='billing_backend_id',
        ),
        migrations.RemoveField(
            model_name='droplet',
            name='last_usage_update_time',
        ),
    ]
