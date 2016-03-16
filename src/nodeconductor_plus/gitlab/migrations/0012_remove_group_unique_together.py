# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gitlab', '0011_unique_spl'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=set([]),
        ),
    ]
