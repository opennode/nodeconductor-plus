# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def delete_duplicates(apps, schema_editor):
    # Ensure uniqueness of DigitalOcean service properties
    for model in ('Image', 'Size', 'Region'):
        cls = apps.get_model('digitalocean', model)
        ids = set()
        for entity in cls.objects.all():
            backend_id = entity.backend_id
            if backend_id in ids:
                entity.delete()
            else:
                ids.add(backend_id)


class Migration(migrations.Migration):

    dependencies = [
        ('digitalocean', '0010_add_creation_states'),
    ]

    operations = [
        migrations.RunPython(delete_duplicates),
        migrations.RemoveField(
            model_name='image',
            name='settings',
        ),
        migrations.RemoveField(
            model_name='region',
            name='settings',
        ),
        migrations.RemoveField(
            model_name='size',
            name='settings',
        ),
        migrations.AlterField(
            model_name='image',
            name='backend_id',
            field=models.CharField(unique=True, max_length=255, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='region',
            name='backend_id',
            field=models.CharField(unique=True, max_length=255, db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='size',
            name='backend_id',
            field=models.CharField(unique=True, max_length=255, db_index=True),
            preserve_default=True,
        ),
    ]
