# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


DEFAULT_PLAN_NAME = 'Default'


def mark_default_plan_from_settings_as_default(apps, schema_editor):
    Plan = apps.get_model('plans', 'Plan')
    Plan.objects.filter(name=DEFAULT_PLAN_NAME).update(is_default=True)


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0010_extend_planquota_choices'),
    ]

    operations = [
        migrations.AddField(
            model_name='plan',
            name='is_default',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.RunPython(mark_default_plan_from_settings_as_default),
    ]
