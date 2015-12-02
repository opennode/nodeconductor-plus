import decimal
import datetime
import mock

from django.utils import timezone
from rest_framework import test, status

from nodeconductor_paypal.models import Invoice
from . import factories
from .. import tasks

class SyncAgreementTest(test.APITransactionTestCase):

    agreement_transaction = {
        'time_stamp': timezone.now(),
        'transaction_id': 'I-0LN988D3JACS',
        'amount': decimal.Decimal(100),
        'payer_email': 'payer@paypal.com'
    }

    def test_transaction_is_added_to_current_invoice(self):
        agreement = factories.AgreementFactory()
        invoice = Invoice.objects.create(
            customer=agreement.customer,
            start_date=timezone.now(),
            end_date=timezone.now() + datetime.timedelta(days=30),
            total_amount=0
        )
        with mock.patch('nodeconductor_plus.plans.tasks.PaypalBackend') as backend:
            backend().get_agreement_transactions.return_value = [self.agreement_transaction]
            tasks.sync_agreement_transactions(agreement.id)

        invoice = Invoice.objects.get(pk=invoice.pk)
        self.assertEqual(invoice.total_amount, self.agreement_transaction['amount'])
        self.assertEqual(invoice.items.count(), 1)
