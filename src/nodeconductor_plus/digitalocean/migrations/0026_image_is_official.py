# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0025_droplet_paid_resource'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='is_official',
            field=models.BooleanField(default=False, help_text='Is image provided by DigitalOcean'),
        ),
    ]
