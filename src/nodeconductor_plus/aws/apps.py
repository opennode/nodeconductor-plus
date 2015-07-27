from django.apps import AppConfig

from nodeconductor.structure import SupportedServices


class AWSConfig(AppConfig):
    name = 'nodeconductor_plus.aws'
    verbose_name = "NodeConductor AWS EC2"

    def ready(self):
        AWSService = self.get_model('AWSService')

        from .backend import AWSBackend
        SupportedServices.register_backend(AWSService, AWSBackend)
