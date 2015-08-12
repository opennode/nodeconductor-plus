from nodeconductor.cost_tracking import CostTrackingStrategy

from .models import Instance


class AWSCostTracking(CostTrackingStrategy):
    RESOURCES = Instance
