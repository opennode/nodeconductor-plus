# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0004_add_creation_states'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='image',
            name='settings',
        ),
        migrations.AlterField(
            model_name='image',
            name='backend_id',
            field=models.CharField(unique=True, max_length=255, db_index=True),
            preserve_default=True,
        ),
    ]
