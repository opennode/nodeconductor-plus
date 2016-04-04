from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models import signals


class PlansConfig(AppConfig):
    name = 'nodeconductor_plus.plans'
    verbose_name = 'NodeConductorPlus Plans'

    def ready(self):
        from . import handlers
        from nodeconductor.structure import models as structure_models

        signals.post_save.connect(
            handlers.create_customer_plan,
            sender=structure_models.Customer,
            dispatch_uid='nodeconductor_plus.plans.handlers.create_customer_plan',
        )
