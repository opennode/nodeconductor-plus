import logging

from nodeconductor.cost_tracking import CostTrackingStrategy
from nodeconductor.structure import ServiceBackendError

from .models import Droplet


logger = logging.getLogger(__name__)


class DigitalOceanCostTracking(CostTrackingStrategy):

    @classmethod
    def get_costs_estimates(cls):
        for droplet in Droplet.objects.exclude(state=Droplet.States.ERRED):
            try:
                backend = droplet.get_backend()
                monthly_cost = backend.get_cost_estimate(droplet.backend_id)
            except ServiceBackendError:
                logger.error("Failed to get price estimate for droplet %s" % droplet)
            else:
                yield droplet, monthly_cost
