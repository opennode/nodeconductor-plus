# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aws', '0002_rename_service_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='awsservice',
            name='available_for_all',
            field=models.BooleanField(default=False, help_text='Service will be automatically added to all customers projects if it is available for all'),
            preserve_default=True,
        ),
    ]