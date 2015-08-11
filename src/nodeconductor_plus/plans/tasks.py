import datetime
import logging

from celery import shared_task
from nodeconductor.billing.backend import BillingBackend, BillingBackendError

from . import models

logger = logging.getLogger(__name__)


@shared_task(name='nodeconductor.plans.check_orders')
def check_orders():
    for order in models.Order.objects.filter(state=models.Order.States.ACTIVE):
        check_order.delay(order.pk)


@shared_task(name='nodeconductor.plans.check_order')
def check_order(order_id):
    order = models.Order.objects.get(pk=order_id)
    backend = BillingBackend()
    transactions = backend.get_agreement_transactions(order.backend_id,
                                                      order.last_transaction_at or order.start_date,
                                                      datetime.datetime.now())
    for transaction in transactions:
        order.customer.credit_account(transaction['amount'])
        order.last_transaction_at = transaction['time_stamp']
        order.save()
