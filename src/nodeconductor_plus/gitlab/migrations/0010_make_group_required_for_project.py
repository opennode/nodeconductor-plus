# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitlab', '0009_group_path_and_spl_unique_together'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='group',
            field=models.ForeignKey(related_name='projects', to='gitlab.Group'),
            preserve_default=True,
        ),
    ]
