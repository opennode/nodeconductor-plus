from django.apps import AppConfig

from nodeconductor.cost_tracking import CostTrackingRegister
from nodeconductor.structure import SupportedServices


class AWSConfig(AppConfig):
    name = 'nodeconductor_plus.aws'
    verbose_name = "NodeConductor AWS EC2"
    service_name = 'Amazon'

    def ready(self):
        from .backend import AWSBackend
        from .cost_tracking import AWSCostTrackingBackend
        SupportedServices.register_backend(AWSBackend)
        CostTrackingRegister.register(self.label, AWSCostTrackingBackend)
