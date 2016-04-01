# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0015_remove_spl_state'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='image_name',
            field=models.CharField(max_length=150, blank=True),
        ),
    ]
