# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0005_image_type_and_distribution'),
    ]

    operations = [
        migrations.AddField(
            model_name='droplet',
            name='ip_address',
            field=models.GenericIPAddressField(null=True, protocol='IPv4', blank=True),
            preserve_default=True,
        ),
    ]
