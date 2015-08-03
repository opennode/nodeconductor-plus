import logging

from celery import shared_task

from nodeconductor.core.tasks import throttle
from nodeconductor.structure import ServiceBackendError, ServiceBackendNotImplemented
from nodeconductor.structure.models import Service
from nodeconductor_plus.insights.log import alert_logger


logger = logging.getLogger(__name__)


@shared_task(name='nodeconductor.insights.check_unmanaged_resources')
def check_unmanaged_resources():
    for model in Service.get_all_models():
        for service in model.objects.all():
            check_service_resources.delay(service.to_string())


@shared_task(is_heavy_task=True)
def check_service_resources(model_string):
    service = next(Service.from_string(model_string))

    try:
        with throttle(key="{}{}".format(service.settings.type, service.settings.backend_url)):
            resources = service.get_backend().get_resources_for_import()
            if len(resources) > 0:
                alert_logger.resource_import.warning('Service {service_name} has unmanaged resources',
                                                     scope=service,
                                                     alert_type='service_has_unmanaged_resources',
                                                     alert_context={'service': service})
            else:
                alert_logger.resource_import.close(scope=service, alert_type='service_has_unmanaged_resources')
    except ServiceBackendError, ServiceBackendNotImplemented:
        logger.warning('Unable to get resources for import')
