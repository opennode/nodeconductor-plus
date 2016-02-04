# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0019_fix_price'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='digitaloceanserviceprojectlink',
            unique_together=set([('service', 'project')]),
        ),
    ]
