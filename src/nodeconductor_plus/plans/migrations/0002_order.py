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
        ('structure', '0006_inherit_namemixin'),
        ('plans', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('customer_name', models.CharField(max_length=150)),
                ('plan_name', models.CharField(max_length=120)),
                ('plan_price', models.DecimalField(max_digits=12, decimal_places=2)),
                ('state', django_fsm.FSMField(default=b'processing', help_text=b'WARNING! Should not be changed manually unless you really know what you are doing.', max_length=20, choices=[(b'processing', b'Processing'), (b'failed', b'Failed'), (b'completed', b'Completed'), (b'erred', b'Erred')])),
                ('customer', models.ForeignKey(to='structure.Customer', null=True)),
                ('plan', models.ForeignKey(related_name='orders', to='plans.Plan', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
