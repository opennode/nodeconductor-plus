from django.apps import AppConfig
from django_fsm.signals import post_transition


class SupportConfig(AppConfig):
    name = 'nodeconductor_plus.premium_support'
    verbose_name = 'NodeConductorPlus Premium Support'

    def ready(self):
        from . import handlers

        Contract = self.get_model('Contract')

        post_transition.connect(
            handlers.log_contract_approved,
            sender=Contract,
            dispatch_uid='nodeconductor.structure.handlers.log_contract_approved',
        )
