import logging

from celery import shared_task

from nodeconductor.core.tasks import throttle
from nodeconductor.structure import ServiceBackendError, ServiceBackendNotImplemented
from nodeconductor.structure.models import Service, ServiceProjectLink
from nodeconductor_plus.insights.log import alert_logger


logger = logging.getLogger(__name__)


@shared_task(name='nodeconductor.insights.check_unmanaged_resources')
def check_unmanaged_resources():
    for model in Service.get_all_models():
        for service in model.objects.all():
            check_service_resources.delay(service.to_string())


@shared_task(is_heavy_task=True)
def check_service_resources(model_string):
    service_model, service_pk = Service.parse_model_string(model_string)
    service = service_model.objects.get(pk=service_pk)

    try:
        open_or_close_unmanaged_resources_alert(service.get_backend(), service)
    except ServiceBackendNotImplemented:
        service_project_links = service.projects.through.objects.filter(service=service)
        for spl in service_project_links:
            check_service_project_link_resources.delay(spl.to_string())


@shared_task(is_heavy_task=True)
def check_service_project_link_resources(model_string):
    spl_model, spl_pk = ServiceProjectLink.parse_model_string(model_string)
    spl = spl_model.objects.get(pk=spl_pk)
    open_or_close_unmanaged_resources_alert(spl.get_backend(), spl.service)


def open_or_close_unmanaged_resources_alert(backend, service):
    try:
        with throttle(concurrency=5):
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
