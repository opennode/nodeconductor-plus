# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('azure', '0004_add_creation_states'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='backend_id',
            field=models.CharField(unique=True, max_length=255),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='image',
            name='settings',
        ),
    ]
