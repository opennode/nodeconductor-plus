# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('azure', '0011_add_min_disk_min_ram_to_vm'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='azureserviceprojectlink',
            name='error_message',
        ),
        migrations.RemoveField(
            model_name='azureserviceprojectlink',
            name='state',
        ),
    ]
