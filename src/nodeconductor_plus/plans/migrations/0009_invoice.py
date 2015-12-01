# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import nodeconductor.logging.log
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0008_change_name_field_in_planquota_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('amount', models.DecimalField(max_digits=9, decimal_places=2)),
                ('date', models.DateField()),
                ('pdf', models.FileField(null=True, upload_to=b'plan-invoices', blank=True)),
                ('backend_id', models.CharField(max_length=255)),
                ('payer_email', models.EmailField(max_length=75)),
                ('agreement', models.ForeignKey(to='plans.Agreement')),
            ],
            options={
                'abstract': False,
            },
            bases=(nodeconductor.logging.log.LoggableMixin, models.Model),
        ),
    ]
