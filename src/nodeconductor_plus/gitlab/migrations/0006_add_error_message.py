# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitlab', '0005_add_creation_states'),
    ]

    operations = [
        migrations.AddField(
            model_name='gitlabserviceprojectlink',
            name='error_message',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
