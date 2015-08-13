from nodeconductor.cost_tracking import CostTrackingStrategy

from .models import VirtualMachine


class AzureCostTracking(CostTrackingStrategy):
    RESOURCES = VirtualMachine
