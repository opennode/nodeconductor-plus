from django.apps import AppConfig

from nodeconductor.cost_tracking import CostTrackingRegister
from nodeconductor.structure import SupportedServices


class DigitalOceanConfig(AppConfig):
    name = 'nodeconductor_plus.digitalocean'
    verbose_name = "NodeConductor DigitalOcean"

    def ready(self):
        DigitalOceanService = self.get_model('DigitalOceanService')

        from .backend import DigitalOceanBackend
        from .cost_tracking import DigitalOceanCostTrackingBackend
        SupportedServices.register_backend(DigitalOceanService, DigitalOceanBackend)
        CostTrackingRegister.register(self.label, DigitalOceanCostTrackingBackend)
