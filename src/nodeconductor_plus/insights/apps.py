from django.apps import AppConfig
from django.db.models import signals

from nodeconductor.quotas.models import Quota
from nodeconductor.structure.models import Customer, Service, Resource
from nodeconductor_plus.insights import handlers


class InsightsConfig(AppConfig):
    name = 'nodeconductor_plus.insights'
    verbose_name = 'NodeConductor Insights'

    def ready(self):

        for index, service in enumerate(Service.get_all_models()):
            signals.post_save.connect(
                handlers.check_unmanaged_resources,
                sender=service,
                dispatch_uid=(
                    'nodeconductor_plus.insights.handlers.check_unmanaged_resources_{}_{}'
                    .format(service.__name__, index))
            )

            signals.post_save.connect(
                handlers.check_managed_services,
                sender=service,
                dispatch_uid=(
                    'nodeconductor_plus.insights.handlers.check_managed_services_{}_{}'
                    .format(service.__name__, index))
            )

        for index, resource in enumerate(Resource.get_all_models()):
            signals.post_delete.connect(
                handlers.check_missed_resources,
                sender=resource,
                dispatch_uid=(
                    'nodeconductor_plus.insights.handlers.check_missed_resources_{}_{}'
                    .format(resource.__name__, index))
            )

        signals.post_save.connect(
            handlers.check_customer_quota_exceeded,
            sender=Quota,
            dispatch_uid='nodeconductor_plus.insights.handlers.check_customer_quota_exceeded'
        )

        signals.post_save.connect(
            handlers.init_managed_services_alert,
            sender=Customer,
            dispatch_uid='nodeconductor_plus.insights.handlers.init_managed_services_alert'
        )
