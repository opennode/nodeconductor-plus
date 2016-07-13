from django.apps import AppConfig
from django.db.models import signals


class DigitalOceanConfig(AppConfig):
    name = 'nodeconductor_plus.digitalocean'
    verbose_name = "NodeConductor DigitalOcean"
    service_name = 'DigitalOcean'
    is_public_service = True

    def ready(self):
        from nodeconductor.core import models as core_models
        from nodeconductor.cost_tracking import CostTrackingRegister
        from nodeconductor.structure import SupportedServices, signals as structure_signals, models as structure_models

        from . import handlers
        from .backend import DigitalOceanBackend
        from .cost_tracking import DigitalOceanCostTrackingBackend
        SupportedServices.register_backend(DigitalOceanBackend)
        CostTrackingRegister.register(self.label, DigitalOceanCostTrackingBackend)

        for model in (structure_models.Project, structure_models.Customer):
            structure_signals.structure_role_revoked.connect(
                handlers.remove_ssh_keys_from_service,
                sender=model,
                dispatch_uid=('nodeconductor_plus.digitalocean.handlers.remove_ssh_keys_from_service__%s'
                              % model.__name__),
            )

        signals.pre_delete.connect(
            handlers.remove_ssh_key_from_service_settings_on_deletion,
            sender=core_models.SshPublicKey,
            dispatch_uid='nodeconductor_plus.digitalocean.handlers.remove_ssh_key_from_service_settings_on_deletion',
        )
