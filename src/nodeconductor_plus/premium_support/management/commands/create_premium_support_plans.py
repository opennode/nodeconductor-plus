from __future__ import unicode_literals

from django.core.management.base import BaseCommand
from django.contrib.webdesign import lorem_ipsum

from ...models import Plan


class Command(BaseCommand):
    help = 'Creates premium support plans'

    def handle(self, *args, **options):
        plans_data = [
            {
                'name': 'Bronze',
                'base_rate': 199.99,
                'hour_rate': 19.99,
            },
            {
                'name': 'Gold',
                'base_rate': 299.99,
                'hour_rate': 29.99,
            },
            {
                'name': 'Platinum',
                'base_rate': 399.99,
                'hour_rate': 39.99,
            },
        ]
        for plan_data in plans_data:
            Plan.objects.get_or_create(description=lorem_ipsum.sentence(),
                                       terms=lorem_ipsum.paragraph(),
                                       **plan_data)
