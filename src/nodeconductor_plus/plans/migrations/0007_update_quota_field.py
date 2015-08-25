# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0006_connect_existed_customers_with_plans_via_agreement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planquota',
            name='name',
            field=models.CharField(max_length=50, choices=[('nc_project_count', 'nc_project_count'), ('nc_resource_count', 'nc_resource_count'), ('nc_user_count', 'nc_user_count'), ('nc_service_count', 'nc_service_count')]),
            preserve_default=True,
        ),
    ]
