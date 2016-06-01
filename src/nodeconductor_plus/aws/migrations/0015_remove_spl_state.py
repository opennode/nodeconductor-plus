# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0014_add_min_disk_min_ram_to_instance'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='awsserviceprojectlink',
            name='error_message',
        ),
        migrations.RemoveField(
            model_name='awsserviceprojectlink',
            name='state',
        ),
    ]
