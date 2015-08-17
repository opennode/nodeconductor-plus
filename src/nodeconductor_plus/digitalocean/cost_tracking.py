from nodeconductor.cost_tracking import CostTrackingStrategy

from .models import Droplet


class DigitalOceanCostTracking(CostTrackingStrategy):
    RESOURCES = Droplet
