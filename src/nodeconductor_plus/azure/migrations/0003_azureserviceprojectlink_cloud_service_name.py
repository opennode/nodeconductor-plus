# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('azure', '0002_azureservice_available_for_all'),
    ]

    operations = [
        migrations.AddField(
            model_name='azureserviceprojectlink',
            name='cloud_service_name',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
    ]
