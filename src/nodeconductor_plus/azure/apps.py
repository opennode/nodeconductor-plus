from django.apps import AppConfig

from nodeconductor.structure import SupportedServices


class AzureConfig(AppConfig):
    name = 'nodeconductor_plus.azure'
    verbose_name = "NodeConductor Azure"

    def ready(self):
        AzureService = self.get_model('AzureService')

        from .backend import AzureBackend
        SupportedServices.register_backend(AzureService, AzureBackend)
