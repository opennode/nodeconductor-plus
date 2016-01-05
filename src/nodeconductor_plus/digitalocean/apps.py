from django.apps import AppConfig

from nodeconductor.cost_tracking import CostTrackingRegister
from nodeconductor.structure import SupportedServices


class DigitalOceanConfig(AppConfig):
    name = 'nodeconductor_plus.digitalocean'
    verbose_name = "NodeConductor DigitalOcean"
    service_name = 'DigitalOcean'

    def ready(self):
        from .backend import DigitalOceanBackend
        from .cost_tracking import DigitalOceanCostTrackingBackend
        SupportedServices.register_backend(DigitalOceanBackend)
        CostTrackingRegister.register(self.label, DigitalOceanCostTrackingBackend)

