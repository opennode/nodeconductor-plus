# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0011_add_is_default'),
    ]

    operations = [
        migrations.AlterField(
            model_name='planquota',
            name='name',
            field=models.CharField(max_length=50, choices=[(b'nc_service_project_link_count', b'nc_service_project_link_count'), (b'nc_private_cloud_count', b'nc_private_cloud_count'), (b'nc_user_count', b'nc_user_count'), (b'nc_app_count', b'nc_app_count'), (b'nc_project_count', b'nc_project_count'), (b'nc_vm_count', b'nc_vm_count'), (b'nc_resource_count', b'nc_resource_count'), (b'nc_service_count', b'nc_service_count')]),
            preserve_default=True,
        ),
    ]
