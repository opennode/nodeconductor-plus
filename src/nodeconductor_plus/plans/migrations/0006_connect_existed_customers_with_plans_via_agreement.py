# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from uuid import uuid4

from django.db import migrations

# This is plan from plans.settings
DEFAULT_PLAN = {
    'name': 'Default',
    'price': 9.99,
    'quotas': (('nc_user_count', 2), ('nc_project_count', 2), ('nc_resource_count', 4),)
}


def connect_existed_customers_with_default_plan(apps, schema_editor):
    Customer = apps.get_model('structure', 'Customer')
    Plan = apps.get_model('plans', 'Plan')
    PlanQuota = apps.get_model('plans', 'PlanQuota')
    Agreement = apps.get_model('plans', 'Agreement')

    if not Plan.objects.filter(name=DEFAULT_PLAN['name'], price=DEFAULT_PLAN['price']).exists():
        default_plan = Plan.objects.create(
            uuid=uuid4().hex, name=DEFAULT_PLAN['name'], price=DEFAULT_PLAN['price'])
        for quota_name, quota_value in DEFAULT_PLAN['quotas']:
            PlanQuota.objects.get_or_create(name=quota_name, value=quota_value, plan=default_plan)

        for customer in Customer.objects.all():
            if not Agreement.objects.filter(customer=customer).exists():
                # We need to add UUID explicitly, because django ignores auto=True parameter in migration UUID field
                Agreement.objects.create(uuid=uuid4().hex, customer=customer, plan=default_plan, state='active')


class Migration(migrations.Migration):

    dependencies = [
        ('plans', '0005_agreement'),
    ]

    operations = [
        migrations.RunPython(connect_existed_customers_with_default_plan)
    ]
