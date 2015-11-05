from nodeconductor.logging.log import EventLogger, event_logger
from nodeconductor.structure.models import Project
from . import models


class PremiumSupportLogger(EventLogger):
    contract = models.Contract

    class Meta:
        event_types = 'contract_approved'


event_logger.register('premium_support', PremiumSupportLogger)
