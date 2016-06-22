import logging

from rest_framework.reverse import reverse

from nodeconductor_paypal.backend import PaypalBackend, PayPalError
from .models import Agreement


logger = logging.getLogger(__name__)


def create_plan_and_agreement(request, agreement):
    """
    Push billing agreement to backend
    """
    backend = PaypalBackend()

    try:
        return_url = reverse('agreement_approve_cb', request=request)
        cancel_url = reverse('agreement_cancel_cb', request=request)

        backend_id = backend.create_plan(
            amount=agreement.plan.price,
            tax=agreement.tax,
            name=agreement.plan.name,
            description=agreement.plan.name,
            return_url=return_url,
            cancel_url=cancel_url)

        approval_url, token = backend.create_agreement(backend_id, agreement.plan.name)
        agreement.set_pending(approval_url, token)
        agreement.save()

        message = 'Agreement for plan %s and customer %s has been pushed to backend'
        logger.info(message, agreement.plan.name, agreement.customer.name)

    except PayPalError as e:
        agreement.set_erred()
        agreement.save()

        message = 'Unable to push agreement for plan %s and customer %s because of backend error %s'
        logger.warning(message, agreement.plan.name, agreement.customer.name, e)


def activate_agreement(agreement):
    """
    Apply quotas for customer according to plan and cancel other active agreement
    """
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
