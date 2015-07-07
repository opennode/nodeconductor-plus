# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import uuidfield.fields
import django_fsm


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0013_servicesettings_customer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('premium_support', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('state', django_fsm.FSMIntegerField(default=1, choices=[(1, b'Requested'), (2, b'Approved'), (3, b'Cancelled')])),
                ('plan', models.ForeignKey(to='premium_support.Plan')),
                ('project', models.ForeignKey(to='structure.Project')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
