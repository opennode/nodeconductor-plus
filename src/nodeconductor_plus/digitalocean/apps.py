from django.apps import AppConfig


class DigitalOceanConfig(AppConfig):
    name = 'nodeconductor_plus.digitalocean'
    verbose_name = "NodeConductor DigitalOcean"
    service_name = 'DigitalOcean'

    def ready(self):
        from nodeconductor.cost_tracking import CostTrackingRegister
        from nodeconductor.structure import SupportedServices

        from .backend import DigitalOceanBackend
        from .cost_tracking import DigitalOceanCostTrackingBackend
        SupportedServices.register_backend(DigitalOceanBackend)
        CostTrackingRegister.register(self.label, DigitalOceanCostTrackingBackend)
