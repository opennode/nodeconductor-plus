import datetime
import logging

from celery import shared_task
from nodeconductor.billing.backend import BillingBackend, BillingBackendError
from nodeconductor_plus.plans.handlers import apply_default_plan
from nodeconductor_plus.plans.models import Agreement

logger = logging.getLogger(__name__)


@shared_task(name='nodeconductor.plans.check_agreements')
def check_agreements():
    for agreement in Agreement.objects.filter(state=Agreement.States.ACTIVE, backend_id__isnull=False):
        check_agreement.delay(agreement.pk)


@shared_task(name='nodeconductor.plans.check_agreement')
def check_agreement(agreement_id):
    """
    Apply default quotas for customer if his current agreement has been cancelled
    """
    agreement = Agreement.objects.get(pk=agreement_id)

    backend = BillingBackend()
    backend_agreement = backend.get_agreement(agreement.backend_id)

    if backend_agreement.state != 'Active':
        agreement.set_cancelled()
        apply_default_plan(agreement.customer)


@shared_task(name='nodeconductor.plans.push_agreement')
def push_agreement(agreement_id):
    agreement = Agreement.objects.get(pk=agreement_id)

    try:
        backend = BillingBackend()
        approval_url, token = backend.create_agreement(agreement.plan.backend_id, agreement.plan.name)
        agreement.set_pending(approval_url, token)
    except BillingBackendError:
        logger.warning('Unable to push agreement because of backend error')
        agreement.set_erred()


@shared_task(name='nodeconductor.plans.activate_agreement')
def activate_agreement(agreement_id):
    agreement = Agreement.objects.get(pk=agreement_id)

    try:
        backend = BillingBackend()
        agreement.backend_id = backend.execute_agreement(agreement.token)
        agreement.save()
        agreement.apply_quotas()
    except BillingBackendError:
        logger.warning('Unable to execute agreement because of backend error')
        agreement.set_erred()

    # Customer should have only one active agreement at time
    # That's why we need to cancel old agreement before activating new one
    try:
        old_agreement = Agreement.objects.get(customer=agreement.customer,
                                              backend_id__isnull=False,
                                              state=Agreement.States.ACTIVE)
        cancel_agreement.delay(old_agreement.pk)
    except Agreement.DoesNotExist:
        logger.info('There is no active agreement for customer')

    agreement.set_active()
    logger.info('New agreement has been activated')


@shared_task(name='nodeconductor.plans.cancel_agreement')
def cancel_agreement(agreement_id):
    agreement = Agreement.objects.get(pk=agreement_id)

    try:
        backend = BillingBackend()
        backend.cancel_agreement(agreement.backend_id)
        agreement.set_cancelled()
        logger.info('Agreement has been cancelled')
    except BillingBackendError:
        logger.warning('Unable to cancel agreement because of backend error')
        agreement.set_erred()
