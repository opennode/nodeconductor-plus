# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodeconductor.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('azure', '0009_add_geoposition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='azureservice',
            name='name',
            field=models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='image',
            name='name',
            field=models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='virtualmachine',
            name='name',
            field=models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name]),
            preserve_default=True,
        ),
    ]
