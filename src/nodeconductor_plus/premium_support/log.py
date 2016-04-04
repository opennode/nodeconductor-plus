from nodeconductor.logging.loggers import EventLogger, event_logger
from . import models


class PremiumSupportLogger(EventLogger):
    contract = models.Contract

    class Meta:
        event_types = 'contract_approved'


event_logger.register('premium_support', PremiumSupportLogger)
