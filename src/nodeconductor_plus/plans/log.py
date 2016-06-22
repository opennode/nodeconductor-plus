from nodeconductor.logging.loggers import EventLogger, event_logger
from .models import Agreement


class PlanAgreementEventLogger(EventLogger):
    payment = Agreement

    class Meta:
        event_types = ('agreement_approve_succeeded',
                       'agreement_cancel_succeeded')
        event_groups = {'payments': event_types}


event_logger.register('plan_agreement', PlanAgreementEventLogger)
