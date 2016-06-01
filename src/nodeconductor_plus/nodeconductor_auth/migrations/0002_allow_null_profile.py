# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def replace_empty_string_to_null(apps, schema_editor):
    AuthProfile = apps.get_model('nodeconductor_auth', 'AuthProfile')
    for profile in AuthProfile.objects.all():
        if profile.google == '':
            profile.google = None
        if profile.facebook == '':
            profile.facebook = None
        profile.save(update_fields=['google', 'facebook'])


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_auth', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='authprofile',
            name='facebook',
            field=models.CharField(max_length=120, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='authprofile',
            name='google',
            field=models.CharField(max_length=120, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.RunPython(replace_empty_string_to_null),
    ]
