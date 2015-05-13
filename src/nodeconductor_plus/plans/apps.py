from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models import signals

from nodeconductor.structure import models as structure_models
from . import handlers


class PlansConfig(AppConfig):
    name = 'nodeconductor_plus.plans'
    verbose_name = 'NodeConductorPlus Plans'

    # See, https://docs.djangoproject.com/en/1.7/ref/applications/#django.apps.AppConfig.ready
    def ready(self):
        signals.post_save.connect(
            handlers.create_customer_plan,
            sender=structure_models.Customer,
            dispatch_uid='nodeconductor_plus.plans.handlers.create_customer_plan',
        )
