# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import django_fsm


def fill_order_username(apps, schema_editor):
    Order = apps.get_model('plans', 'Order')

    for order in Order.objects.filter(user__isnull=False):
        order.username = order.user.username
        order.save()


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0004_connect_existed_customers_with_plans'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='approval_url',
            field=models.URLField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='backend_id',
            field=models.CharField(max_length=255, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='end_date',
            field=models.DateTimeField(help_text=b'Date when order has been cancelled', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='start_date',
            field=models.DateTimeField(help_text=b'Date when order has been activated', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='token',
            field=models.CharField(max_length=120, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='username',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.RunPython(fill_order_username),
        migrations.AddField(
            model_name='plan',
            name='backend_id',
            field=models.CharField(max_length=255, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='customer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='structure.Customer', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='plan',
            field=models.ForeignKey(related_name='orders', on_delete=django.db.models.deletion.SET_NULL, to='plans.Plan', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='state',
            field=django_fsm.FSMField(default=b'created', help_text=b'WARNING! Should not be changed manually unless you really know what you are doing.', max_length=20, choices=[(b'created', b'Created'), (b'pending', b'Pending'), (b'active', b'Active'), (b'cancelled', b'Cancelled'), (b'erred', b'Erred')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='last_transaction_at',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
    ]
