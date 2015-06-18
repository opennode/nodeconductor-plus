# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0003_remove_auth_token_field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='settings',
            field=models.ForeignKey(related_name='+', blank=True, to='structure.ServiceSettings', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='region',
            name='settings',
            field=models.ForeignKey(related_name='+', blank=True, to='structure.ServiceSettings', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='size',
            name='settings',
            field=models.ForeignKey(related_name='+', blank=True, to='structure.ServiceSettings', null=True),
            preserve_default=True,
        ),
    ]
