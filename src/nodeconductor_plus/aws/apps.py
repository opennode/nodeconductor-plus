from django.apps import AppConfig


class AWSConfig(AppConfig):
    name = 'nodeconductor_plus.aws'
    verbose_name = "NodeConductor AWS EC2"
    service_name = 'Amazon'
    is_public_service = True

    def ready(self):
        from nodeconductor.cost_tracking import CostTrackingRegister
        from nodeconductor.structure import SupportedServices

        from .backend import AWSBackend
        from .cost_tracking import AWSCostTrackingBackend
        SupportedServices.register_backend(AWSBackend)
        CostTrackingRegister.register(self.label, AWSCostTrackingBackend)
