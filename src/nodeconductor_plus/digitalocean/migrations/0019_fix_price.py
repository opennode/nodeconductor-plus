# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0018_size_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='size',
            name='price',
            field=models.DecimalField(default=0, verbose_name='Hourly price rate', max_digits=11, decimal_places=5),
            preserve_default=True,
        ),
    ]
