# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0015_add_ip_fields'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='droplet',
            name='ip_address',
        ),
    ]
