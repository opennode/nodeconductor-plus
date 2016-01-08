import logging
import datetime

from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from nodeconductor.core.tasks import throttle
from nodeconductor.structure import SupportedServices, ServiceBackendError, ServiceBackendNotImplemented
from nodeconductor.structure.models import Customer, Service
from nodeconductor.cost_tracking.models import PriceEstimate
from nodeconductor_plus.insights.log import alert_logger


logger = logging.getLogger(__name__)


@shared_task(name='nodeconductor.insights.check_services')
def check_services():
    for model in Service.get_all_models():
        for service in model.objects.all():
            if not service.settings.shared:  # resources import from shared services is not available
                check_service_resources.delay(service.to_string())
            check_service_availability.delay(service.to_string())
            check_service_resources_availability.delay(service.to_string())


@shared_task(name='nodeconductor.insights.check_customers')
def check_customers():
    for customer in Customer.objects.exclude(billing_backend_id=''):
        check_customer_costs.delay(customer.uuid)


@shared_task(is_heavy_task=True)
def check_service_resources(service_str):
    try:
        service = next(Service.from_string(service_str))
    except StopIteration:
        logger.warning('Missing service %s.', service_str)
        return

    erred = False
    with throttle(key="{}{}".format(service.settings.type, service.settings.backend_url)):
        for service_project_link in service.get_service_project_links():
            try:
                resources = service_project_link.get_backend().get_resources_for_import()
                if len(resources) > 0:
                    alert_logger.service_state.warning(
                        'Service {service_name} has unmanaged resources',
                        scope=service,
                        alert_type='service_has_unmanaged_resources',
                        alert_context={'service': service})
                    return
            except (ServiceBackendError, ServiceBackendNotImplemented) as exception:
                logger.warning(
                    'Unable to check unmanaged resources for service project link %s: %s',
                    service_project_link.to_string(),
                    exception)
                erred = True
    if not erred:
        alert_logger.service_state.close(scope=service, alert_type='service_has_unmanaged_resources')


@shared_task
def check_service_availability(service_str):
    try:
        service = next(Service.from_string(service_str))
    except StopIteration:
        logger.warning('Missing service %s.', service_str)
        return

    backend = service.get_backend()

    try:
        available = backend.ping()
    except ServiceBackendNotImplemented:
        logger.error("Method ping() is not implemented for %s" % backend.__class__.__name__)
        available = True
    except ServiceBackendError:
        available = False

    if not available:
        alert_logger.service_state.warning(
            'Service account {service_name} is not responding',
            scope=service,
            alert_type='service_unavailable',
            alert_context={'service': service})
    else:
        alert_logger.service_state.close(scope=service, alert_type='service_unavailable')


@shared_task
def check_service_resources_availability(service_str):
    try:
        service = next(Service.from_string(service_str))
    except StopIteration:
        logger.warning('Missing service %s.', service_str)
        return

    for resource_model in SupportedServices.get_service_resources(service):
        for resource in resource_model.objects.filter(
                service_project_link__service=service).exclude(backend_id=''):
            backend = resource.get_backend()
            try:
                available = backend.ping_resource(resource)
            except ServiceBackendNotImplemented:
                logger.error("Method ping_resource() is not implemented for %s" % backend.__class__.__name__)
                available = True
            except ServiceBackendError as exception:
                available = False
                logger.warning('Unable to ping resource %s: %s', resource.to_string(), exception)

            if not available:
                alert_logger.resource_state.warning(
                    'Resource {resource_name} has disappeared from the backend',
                    scope=resource,
                    alert_type='resource_disappeared_from_backend',
                    alert_context={'resource': resource})
            else:
                alert_logger.resource_state.close(scope=resource, alert_type='resource_disappeared_from_backend')


@shared_task
def check_customer_costs(customer_uuid):
    try:
        customer = Customer.objects.get(uuid=customer_uuid)
    except Customer.DoesNotExist:
        logger.warning('Customer does not exist %s.', customer_uuid)
        return

    try:
        dt_now = datetime.datetime.now()
        costs_now = PriceEstimate.objects.get(scope=customer, month=dt_now.month, year=dt_now.year)

        dt_prev = dt_now - datetime.timedelta(months=1)
        costs_prev = PriceEstimate.objects.get(scope=customer, month=dt_prev.month, year=dt_prev.year)
    except PriceEstimate.DoesNotExist:
        pass
    else:
        nc_settings = getattr(settings, 'NODECONDUCTOR_PLUS', {})
        max_excess = nc_settings.get('PROJECTED_COSTS_EXCESS')

        try:
            excess = 100 * (1 - costs_prev.total / costs_now.total)
        except ZeroDivisionError:
            pass
        else:
            if max_excess:
                if excess >= max_excess:
                    alert_logger.customer_state.warning(
                        'This month estimated costs for customer {customer_name} exceeded',
                        scope=customer,
                        alert_type='customer_projected_costs_exceeded',
                        alert_context={'customer': customer})
                else:
                    alert_logger.customer_state.close(
                        scope=customer, alert_type='customer_projected_costs_exceeded')
