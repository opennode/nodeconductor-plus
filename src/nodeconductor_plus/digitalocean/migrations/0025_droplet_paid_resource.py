# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0024_droplet_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='droplet',
            name='billing_backend_id',
            field=models.CharField(help_text='ID of a resource in backend', max_length=255, blank=True),
        ),
        migrations.AddField(
            model_name='droplet',
            name='last_usage_update_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
