# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authprofile',
            name='facebook',
            field=models.CharField(unique=True, max_length=120, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='authprofile',
            name='google',
            field=models.CharField(unique=True, max_length=120, blank=True),
            preserve_default=True,
        ),
    ]
