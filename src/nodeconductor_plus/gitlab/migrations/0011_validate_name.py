# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodeconductor.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('gitlab', '0010_make_group_required_for_project'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gitlabservice',
            name='name',
            field=models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='group',
            name='name',
            field=models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=150, verbose_name='name', validators=[nodeconductor.core.validators.validate_name]),
            preserve_default=True,
        ),
    ]
