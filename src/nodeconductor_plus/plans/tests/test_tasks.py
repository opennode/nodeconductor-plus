import decimal
import datetime
import mock

from django.utils import timezone
from rest_framework import test, status

from nodeconductor_paypal.models import Invoice
from . import factories
from .. import tasks


class GenerateInvoicesTest(test.APITransactionTestCase):

    agreement_transaction = {
        'time_stamp': timezone.now(),
        'transaction_id': 'I-0LN988D3JACS',
        'amount': decimal.Decimal(100),
        'payer_email': 'payer@paypal.com'
    }

    def test_transaction_is_added_to_current_invoice(self):
        agreement = factories.AgreementFactory()
        with mock.patch('nodeconductor_plus.plans.tasks.PaypalBackend') as backend:
            with mock.patch('nodeconductor_plus.plans.tasks.Invoice.generate_pdf') as generate_pdf:
                backend().get_agreement_transactions.return_value = [self.agreement_transaction]
                tasks.generate_agreement_invoices(agreement.id)
                generate_pdf.assert_called_once_with()

        invoice = Invoice.objects.first()
        self.assertEqual(invoice.total_amount, self.agreement_transaction['amount'])
        self.assertEqual(invoice.items.count(), 1)
