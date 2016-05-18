
from django.contrib.contenttypes.models import ContentType

from nodeconductor.structure.models import Customer
from nodeconductor_plus.insights.tasks import check_service_resources
from nodeconductor_plus.insights.log import alert_logger


# XXX: This handlers should be moved to applications configurations and should be supported by quota application.
# Issue: NC-920

def check_unmanaged_resources(sender, instance, created=False, **kwargs):
    if created and not instance.settings.shared:
        check_service_resources.delay(instance.to_string())


def check_managed_services(sender, instance, created=False, **kwargs):
    if created:
        alert_logger.customer_state.close(scope=instance.customer, alert_type='customer_has_zero_services')


def check_managed_resources(sender, instance, created=False, **kwargs):
    if created:
        alert_logger.customer_state.close(scope=instance.customer, alert_type='customer_has_zero_resources')


def check_managed_projects(sender, instance, created=False, **kwargs):
    if created:
        alert_logger.customer_state.close(scope=instance.customer, alert_type='customer_has_zero_projects')


def init_managed_services_alert(sender, instance, created=False, **kwargs):
    if created:
        log_managed_services_alert(instance)


def init_managed_resources_alert(sender, instance, created=False, **kwargs):
    if created:
        log_managed_resources_alert(instance)


def init_managed_projects_alert(sender, instance, created=False, **kwargs):
    if created:
        log_managed_projects_alert(instance)


def log_managed_services_alert(customer):
    alert_logger.customer_state.warning(
        'Customer {customer_name} has zero services configured.',
        scope=customer,
        alert_type='customer_has_zero_services',
        alert_context={'customer': customer})


def log_managed_resources_alert(customer):
    alert_logger.customer_state.warning(
        'Customer {customer_name} does not have any resources.',
        scope=customer,
        alert_type='customer_has_zero_resources',
        alert_context={'customer': customer})


def log_managed_projects_alert(customer):
    alert_logger.customer_state.warning(
        'Customer {customer_name} does not have any projects.',
        scope=customer,
        alert_type='customer_has_zero_projects',
        alert_context={'customer': customer})


def check_customer_quota_exceeded(sender, instance, **kwargs):
    # XXX: it's partialy duplicates 'quota_usage_is_over_threshold' alert

    # XXX: Hotfix: do not execute signal if quota scope is None.
    if instance.scope is None:
        return

    AFFECTED_QUOTAS = ('nc_project_count', 'nc_resource_count', 'nc_service_count')

    customer_content_type = ContentType.objects.get_for_model(Customer)
    if instance.content_type == customer_content_type and instance.name in AFFECTED_QUOTAS:
        alert_type = instance.name.replace('nc_', 'customer_') + '_exceeded'
        if instance.is_exceeded():
            alert_logger.quota_check.warning(
                'Customer {customer_name} has exceeded quota {quota_name}.',
                scope=instance.scope,
                alert_type=alert_type,
                alert_context={'customer': instance.scope, 'quota_name': instance.name})
        else:
            alert_logger.quota_check.close(scope=instance.scope, alert_type=alert_type)

        if instance.name == 'nc_service_count' and instance.usage == 0:
            log_managed_services_alert(instance.scope)

        if instance.name == 'nc_resource_count' and instance.usage == 0:
            log_managed_resources_alert(instance.scope)

        if instance.name == 'nc_project_count' and instance.usage == 0:
            log_managed_projects_alert(instance.scope)
