# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0022_remove_spl_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='droplet',
            name='image_name',
            field=models.CharField(max_length=150, blank=True),
        ),
    ]
