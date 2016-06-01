# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0023_droplet_image_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='droplet',
            name='runtime_state',
            field=models.CharField(max_length=150, verbose_name='runtime state', blank=True),
        ),
        migrations.AlterField(
            model_name='droplet',
            name='state',
            field=django_fsm.FSMIntegerField(default=5, choices=[(5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Update Scheduled'), (2, 'Updating'), (7, 'Deletion Scheduled'), (8, 'Deleting'), (3, 'OK'), (4, 'Erred')]),
        ),
    ]
