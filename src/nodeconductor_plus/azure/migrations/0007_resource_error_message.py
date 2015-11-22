# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('azure', '0006_add_error_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='virtualmachine',
            name='error_message',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
