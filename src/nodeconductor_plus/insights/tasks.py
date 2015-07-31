import logging

from celery import shared_task

from nodeconductor.structure import ServiceBackendError
from nodeconductor.structure.models import Service
from nodeconductor_plus.insights.log import alert_logger


logger = logging.getLogger(__name__)


@shared_task(name='nodeconductor_plus.insights.check_unmanaged_resources')
def check_unmanaged_resources():
    for model in Service.get_all_models():
        for service in model.objects.all():
            backend = service.get_backend()
            try:
                resources = backend.get_resources_for_import()
                if len(resources) > 0:
                    alert_logger.resource_import.warning('Service {service_name} has unmanaged resources',
                                                         scope=service,
                                                         alert_type='service_has_unmanaged_resources',
                                                         alert_context={'service': service})
                else:
                    alert_logger.resource_import.close(scope=service, alert_type='service_has_unmanaged_resources')
            except ServiceBackendError:
                logger.warning('Unable to get resources for import')
                continue
