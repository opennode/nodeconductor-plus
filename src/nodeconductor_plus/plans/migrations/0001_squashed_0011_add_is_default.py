# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_fsm
import django.utils.timezone
from django.conf import settings
import nodeconductor.core.fields
import model_utils.fields


class Migration(migrations.Migration):

    replaces = [('plans', '0001_initial'), ('plans', '0002_order'), ('plans', '0003_plancustomer_uuid'), ('plans', '0004_connect_existed_customers_with_plans'), ('plans', '0005_agreement'), ('plans', '0006_connect_existed_customers_with_plans_via_agreement'), ('plans', '0007_update_quota_field'), ('plans', '0008_change_name_field_in_planquota_model'), ('plans', '0009_allow_blank'), ('plans', '0010_extend_planquota_choices'), ('plans', '0011_add_is_default')]

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('structure', '0001_squashed_0021_balancehistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='Plan',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('name', models.CharField(max_length=120)),
                ('price', models.DecimalField(max_digits=12, decimal_places=2)),
                ('backend_id', models.CharField(max_length=255, null=True)),
                ('is_default', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PlanQuota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50, choices=[('nc_project_count', 'nc_project_count'), ('nc_resource_count', 'nc_resource_count'), ('nc_app_count', 'nc_app_count'), ('nc_vm_count', 'nc_vm_count'), ('nc_user_count', 'nc_user_count'), ('nc_service_project_link_count', 'nc_service_project_link_count'), ('nc_service_count', 'nc_service_count')])),
                ('value', models.FloatField()),
                ('plan', models.ForeignKey(related_name='quotas', to='plans.Plan')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='planquota',
            unique_together=set([('plan', 'name')]),
        ),
        migrations.CreateModel(
            name='Agreement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, verbose_name='created', editable=False)),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, verbose_name='modified', editable=False)),
                ('uuid', nodeconductor.core.fields.UUIDField()),
                ('backend_id', models.CharField(max_length=255, null=True, blank=True)),
                ('token', models.CharField(max_length=120, null=True, blank=True)),
                ('approval_url', models.URLField(null=True, blank=True)),
                ('state', django_fsm.FSMField(default=b'created', help_text=b'WARNING! Should not be changed manually unless you really know what you are doing.', max_length=20, choices=[(b'created', b'Created'), (b'pending', b'Pending'), (b'approved', b'Approved'), (b'active', b'Active'), (b'cancelled', b'Cancelled'), (b'erred', b'Erred')])),
                ('customer', models.ForeignKey(to='structure.Customer')),
                ('plan', models.ForeignKey(to='plans.Plan')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-modified'],
                'abstract': False,
            },
        ),
    ]
