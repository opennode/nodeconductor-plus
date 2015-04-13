from __future__ import unicode_literals

from django.core.management.base import BaseCommand

from ...models import Plan, PlanQuota


class Command(BaseCommand):
    help = 'Creates plans: Default, Small, Medium, Large'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'Default',
                'price': 9.99,
                'quotas': (('nc_user_count', 2), ('nc_project_count', 2), ('nc_resource_count', 4),)
            },
            {
                'name': 'Small',
                'price': 19.99,
                'quotas': (('nc_user_count', 10), ('nc_project_count', 10), ('nc_resource_count', 40),)
            },
            {
                'name': 'Medium',
                'price': 29.99,
                'quotas': (('nc_user_count', 30), ('nc_project_count', 30), ('nc_resource_count', 100),)
            },
            {
                'name': 'Large',
                'price': 49.99,
                'quotas': (('nc_user_count', 100), ('nc_project_count', 100), ('nc_resource_count', 1000),)
            },
        ]
        for plan_data in plans_data:
            plan, created = Plan.objects.get_or_create(name=plan_data['name'], price=plan_data['price'])
            if created:
                self.stdout.write('Plan "%s" was created' % plan)
            else:
                self.stdout.write('Plan "%s" already exists' % plan)
            for quota_name, quota_value in plan_data['quotas']:
                PlanQuota.objects.get_or_create(name=quota_name, value=quota_value, plan=plan)
