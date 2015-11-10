# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0011_unique_backend_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='digitaloceanserviceprojectlink',
            name='error_message',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
