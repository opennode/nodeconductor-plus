import logging

from celery import shared_task
from dateutil.relativedelta import relativedelta
from nodeconductor_paypal.backend import PaypalBackend, PayPalError
from nodeconductor_paypal.models import Invoice, InvoiceItem
from nodeconductor_plus.plans.models import Agreement


logger = logging.getLogger(__name__)


@shared_task(name='nodeconductor.plans.check_agreements')
def check_agreements():
    for agreement in Agreement.objects.filter(state=Agreement.States.ACTIVE, backend_id__isnull=False):
        check_agreement.delay(agreement.pk)


@shared_task(name='nodeconductor.plans.check_agreement')
def check_agreement(agreement_id):
    """
    Check if agreement has been cancelled in backend and then apply default quotas for customer
    """
    agreement = Agreement.objects.get(pk=agreement_id)
    backend = PaypalBackend()

    try:
        backend_agreement = backend.get_agreement(agreement.backend_id)
        if backend_agreement.state != 'Active':
            agreement.set_cancelled()
            agreement.save()
            Agreement.apply_default_plan(agreement.customer)
    except PayPalError:
        agreement.set_erred()
        agreement.save()
        logger.warning('Unable to fetch agreement from backend %s', agreement.backend_id)


@shared_task(name='nodeconductor.plans.sync_agreement')
def sync_agreement(agreement_id):
    agreement = Agreement.objects.get(pk=agreement_id)
    push_agreement(agreement)


def push_agreement(agreement):
    """
    Push billing agreement to backend
    """
    backend = PaypalBackend()

    try:
        approval_url, token = backend.create_agreement(agreement.plan.backend_id, agreement.plan.name)
        agreement.set_pending(approval_url, token)
        agreement.save()

        message = 'Agreement for plan %s and customer %s has been pushed to backend'
        logger.info(message, agreement.plan.name, agreement.customer.name)

    except PayPalError:
        agreement.set_erred()
        agreement.save()

        message = 'Unable to push agreement for plan %s and customer %s because of backend error'
        logger.warning(message, agreement.plan.name, agreement.customer.name)


@shared_task(name='nodeconductor.plans.activate_agreement')
def activate_agreement(agreement_id):
    """
    Apply quotas for customer according to plan and cancel other active agreement
    """
    agreement = Agreement.objects.get(pk=agreement_id)
    backend = PaypalBackend()

    try:
        agreement.backend_id = backend.execute_agreement(agreement.token)
        message = 'Agreement for plan %s and customer %s has been activated'
        logger.info(message, agreement.plan.name, agreement.customer.name)

    except PayPalError:
        agreement.set_erred()
        agreement.save()

        message = 'Unable to execute agreement for plan %s and customer %s because of backend error'
        logger.warning(message, agreement.plan.name, agreement.customer.name)

    # Customer should have only one active agreement at time
    # That's why we need to cancel old agreement before activating new one
    try:
        old_agreement = Agreement.objects.get(customer=agreement.customer,
                                              backend_id__isnull=False,
                                              state=Agreement.States.ACTIVE)
        cancel_agreement(old_agreement)
    except Agreement.DoesNotExist:
        logger.info('There is no active agreement for customer')

    agreement.apply_quotas()
    agreement.set_active()
    agreement.save()
    logger.info('New agreement has been activated')


def cancel_agreement(agreement):
    """
    Cancel active agreement
    """
    backend = PaypalBackend()

    try:
        backend.cancel_agreement(agreement.backend_id)
        agreement.set_cancelled()
        agreement.save()

        message = 'Agreement for plan %s and customer %s has been cancelled'
        logger.info(message, agreement.plan.name, agreement.customer.name)

    except PayPalError:
        agreement.set_erred()
        agreement.save()

        message = 'Unable to cancel agreement for plan %s and customer %s because of backend error'
        logger.warning(message, agreement.plan.name, agreement.customer.name)


@shared_task(name='nodeconductor.plans.generate_agreement_invoices')
def generate_agreement_invoices(agreement_id):
    try:
        agreement = Agreement.objects.get(pk=agreement_id)
    except Agreement.DoesNotExist:
        logger.warning('Missing agreement with id %s', agreement.id)
        return

    try:
        txs = PaypalBackend().get_agreement_transactions(
            agreement.backend_id, agreement.created)
    except PayPalError as e:
        message = 'Unable to fetch transactions for billing plan agreement with id %s: %s'
        logger.warning(message, agreement.id, e)
        return

    nc_items = set(InvoiceItem.objects.exclude(backend_id__isnull=True).values_list('backend_id', flat=True))
    for tx in txs:
        backend_id = tx['transaction_id']
        # Skip transactions which are already stored in database
        if backend_id in nc_items:
            continue

        start_date = tx['time_stamp']
        end_date = start_date + relativedelta(month=1)
        amount = tx['amount']
        description = 'Monthly fee for %s plan' % agreement.plan.name

        invoice = Invoice.objects.create(
            customer=agreement.customer,
            start_date=start_date,
            end_date=end_date,
            total_amount=amount)

        InvoiceItem.objects.create(invoice=invoice,
                                   created_at=start_date,
                                   amount=amount,
                                   backend_id=backend_id,
                                   description=description)

        invoice.generate_pdf()
