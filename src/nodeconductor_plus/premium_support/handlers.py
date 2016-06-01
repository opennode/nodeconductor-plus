from .models import Contract
from .log import event_logger


def log_contract_approved(sender, instance, name, source, target, **kwargs):
    if target != Contract.States.APPROVED:
        return

    event_logger.premium_support.info(
        'Premium support contract for project {project_name} and plan {plan_name} has been approved.',
        event_type='contract_approved',
        event_context={'contract': instance})
