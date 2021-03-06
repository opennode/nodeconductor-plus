from django.apps import AppConfig
from django.db.models import signals


class InsightsConfig(AppConfig):
    name = 'nodeconductor_plus.insights'
    verbose_name = 'NodeConductor Insights'

    def ready(self):
        from nodeconductor.quotas.models import Quota
        from nodeconductor.structure.models import Customer, Service, ResourceMixin, Project
        from nodeconductor_plus.insights import handlers

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

        for index, resource in enumerate(ResourceMixin.get_all_models()):
            signals.post_save.connect(
                handlers.check_managed_resources,
                sender=resource,
                dispatch_uid=(
                    'nodeconductor_plus.insights.handlers.check_managed_resources_{}_{}'
                    .format(resource.__name__, index))
            )

        signals.post_save.connect(
            handlers.check_managed_projects,
            sender=Project,
            dispatch_uid='nodeconductor_plus.insights.handlers.check_managed_projects'
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

        signals.post_save.connect(
            handlers.init_managed_resources_alert,
            sender=Customer,
            dispatch_uid='nodeconductor_plus.insights.handlers.init_managed_resources_alert'
        )

        signals.post_save.connect(
            handlers.init_managed_projects_alert,
            sender=Customer,
            dispatch_uid='nodeconductor_plus.insights.handlers.init_managed_projects_alert'
        )
