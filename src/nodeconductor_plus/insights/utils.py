import logging

from nodeconductor.structure import ServiceBackendError
from nodeconductor_plus.insights.log import alert_logger

logger = logging.getLogger(__name__)


def check_service(service):
    try:
        backend = service.get_backend()
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
