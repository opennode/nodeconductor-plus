from django.apps import AppConfig
from django.db.models import signals

from nodeconductor.cost_tracking import CostTrackingRegister
from nodeconductor.structure import SupportedServices

from . import handlers


class DigitalOceanConfig(AppConfig):
    name = 'nodeconductor_plus.digitalocean'
    verbose_name = "NodeConductor DigitalOcean"
    service_name = 'DigitalOcean'

    def ready(self):
        from .backend import DigitalOceanBackend
        from .cost_tracking import DigitalOceanCostTrackingBackend
        SupportedServices.register_backend(DigitalOceanBackend)
        CostTrackingRegister.register(self.label, DigitalOceanCostTrackingBackend)

        Droplet = self.get_model('Droplet')
        signals.post_save.connect(
            handlers.log_read_only_token_alert,
            sender=Droplet,
            dispatch_uid='nodeconductor_plus.digitalocean.handlers.log_read_only_token_alert'
        )
