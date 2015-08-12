# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import model_utils.fields
import django.utils.timezone
from django.conf import settings
import django_fsm
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('plans', '0004_connect_existed_customers_with_plans'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agreement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('backend_id', models.CharField(max_length=255, null=True)),
                ('token', models.CharField(max_length=120, null=True)),
                ('approval_url', models.URLField(null=True)),
                ('start_date', models.DateTimeField(help_text=b'Date when agreement has been activated', null=True)),
                ('end_date', models.DateTimeField(help_text=b'Date when agreement has been cancelled', null=True)),
                ('state', django_fsm.FSMField(default=b'created', help_text=b'WARNING! Should not be changed manually unless you really know what you are doing.', max_length=20, choices=[(b'created', b'Created'), (b'pending', b'Pending'), (b'approved', b'Approved'), (b'active', b'Active'), (b'cancelled', b'Cancelled'), (b'erred', b'Erred')])),
                ('customer', models.ForeignKey(to='structure.Customer')),
                ('plan', models.ForeignKey(to='plans.Plan')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='Order',
        ),
        migrations.DeleteModel(
            name='PlanCustomer',
        ),
    ]
