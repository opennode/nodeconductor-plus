from django.apps import AppConfig

from nodeconductor.cost_tracking import CostTrackingRegister
from nodeconductor.structure import SupportedServices


class AzureConfig(AppConfig):
    name = 'nodeconductor_plus.azure'
    verbose_name = "NodeConductor Azure"

    def ready(self):
        AzureService = self.get_model('AzureService')

        from .backend import AzureBackend
        from .cost_tracking import AzureCostTrackingBackend
        SupportedServices.register_backend(AzureService, AzureBackend)
        CostTrackingRegister.register(self.label, AzureCostTrackingBackend)
