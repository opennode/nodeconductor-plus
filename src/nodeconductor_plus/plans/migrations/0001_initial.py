# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuidfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0005_init_customers_quotas'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', uuidfield.fields.UUIDField(unique=True, max_length=32, editable=False, blank=True)),
                ('name', models.CharField(max_length=120)),
                ('price', models.DecimalField(max_digits=12, decimal_places=2)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlanCustomer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('customer', models.OneToOneField(related_name='+', to='structure.Customer')),
                ('plan', models.ForeignKey(related_name='plan_customers', to='plans.Plan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PlanQuota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, choices=[('nc_project_count', 'nc_project_count'), ('nc_resource_count', 'nc_resource_count'), ('nc_user_count', 'nc_user_count')])),
                ('value', models.FloatField()),
                ('plan', models.ForeignKey(related_name='quotas', to='plans.Plan')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='planquota',
            unique_together=set([('plan', 'name')]),
        ),
    ]
