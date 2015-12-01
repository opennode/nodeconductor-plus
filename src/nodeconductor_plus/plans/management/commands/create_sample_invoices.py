from __future__ import unicode_literals

from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from nodeconductor.structure.models import Customer
from ...models import Plan, Agreement, Invoice


class Command(BaseCommand):
    args = '<customer_id>'
    help = 'Creates sample invoices'

    def handle(self, *args, **options):
        if Plan.objects.count() == 0:
            raise CommandError('Plans are not yet created. Run `createsampleplans` first.')

        if len(args) == 0:
            raise CommandError('Customer ID is not specified.')

        try:
            customer = Customer.objects.get(id=args[0])
        except Customer.DoesNotExist:
            raise CommandError('Customer is not found.')

        if not Agreement.objects.filter(customer=customer).exists():
            Agreement.apply_default_plan(customer)

        agreement = Agreement.objects.filter(customer=customer).last()

        for i in range(10):
            Invoice.objects.create(
                agreement=agreement,
                amount=100 + i * 10,
                date=timezone.now() - timedelta(days=i),
                backend_id='TRANSACTION_ID',
                payer_email='payer@paypal.com')
