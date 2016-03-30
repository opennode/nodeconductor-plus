# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gitlab', '0012_remove_group_unique_together'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gitlabserviceprojectlink',
            name='error_message',
        ),
        migrations.RemoveField(
            model_name='gitlabserviceprojectlink',
            name='state',
        ),
    ]
