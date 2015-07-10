from django.apps import AppConfig

from nodeconductor.structure import SupportedServices


class DigitalOceanConfig(AppConfig):
    name = 'nodeconductor_plus.digitalocean'
    verbose_name = "NodeConductor DigitalOcean"

    def ready(self):
        DigitalOceanService = self.get_model('DigitalOceanService')

        from .backend import DigitalOceanBackend
        SupportedServices.register_backend(DigitalOceanService, DigitalOceanBackend)
