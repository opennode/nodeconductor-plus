from django.apps import AppConfig

from nodeconductor.structure import SupportedServices


class DigitalOceanConfig(AppConfig):
    name = 'nodeconductor_plus.digitalocean'
    verbose_name = "NodeConductor DigitalOcean"

    def ready(self):
        Service = self.get_model('Service')

        from .backend import DigitalOceanBackend
        SupportedServices.register_backend(Service, DigitalOceanBackend)
