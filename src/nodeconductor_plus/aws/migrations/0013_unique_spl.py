# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0012_fix_price'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='awsserviceprojectlink',
            unique_together=set([('service', 'project')]),
        ),
    ]
