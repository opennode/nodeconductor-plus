import logging

from celery import shared_task
from nodeconductor_paypal.backend import PaypalBackend, PayPalError
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
