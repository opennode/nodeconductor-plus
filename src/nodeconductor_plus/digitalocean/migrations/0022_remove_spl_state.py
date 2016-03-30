# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0021_add_min_disk_min_ram_to_droplet'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='digitaloceanserviceprojectlink',
            name='error_message',
        ),
        migrations.RemoveField(
            model_name='digitaloceanserviceprojectlink',
            name='state',
        ),
    ]
