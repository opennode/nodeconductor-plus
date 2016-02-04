# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('azure', '0009_add_geoposition'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='azureserviceprojectlink',
            unique_together=set([('service', 'project')]),
        ),
    ]
