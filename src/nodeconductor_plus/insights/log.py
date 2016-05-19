from nodeconductor.logging.loggers import AlertLogger, alert_logger


class ServiceStateAlertLogger(AlertLogger):
    service = 'structure.Service'

    class Meta:
        alert_types = ('service_has_unmanaged_resources',
                       'service_unavailable')
        alert_groups = {
            'resources': ('service_has_unmanaged_resources',),
            'services': (
                'service_unavailable',
                'service_has_unmanaged_resources'
            )
        }


class ResourceStateAlertLogger(AlertLogger):
    resource = 'structure.ResourceMixin'

    class Meta:
        alert_types = ('resource_disappeared_from_backend',)
        alert_groups = {
            'resources': alert_types
        }


class CustomerStateAlertLogger(AlertLogger):
    customer = 'structure.Customer'

    class Meta:
        alert_types = ('customer_has_zero_services',
                       'customer_has_zero_resources',
                       'customer_has_zero_projects',
                       'customer_projected_costs_exceeded')
        alert_groups = {
            'services': ('customer_has_zero_services',),
            'resources': ('customer_has_zero_resources',),
            'projects': (
                'customer_has_zero_projects',
                'customer_project_count_exceeded'
            ),
            'quota': ('customer_projected_costs_exceeded',)
        }


class QuotaCheckAlertLogger(AlertLogger):
    customer = 'structure.Customer'
    quota_name = basestring

    class Meta:
        alert_types = ('customer_project_count_exceeded',
                       'customer_resource_count_exceeded',
                       'customer_service_count_exceeded')
        alert_groups = {
            'resources': ('customer_resource_count_exceeded',),
            'services': ('customer_service_count_exceeded', )
        }


alert_logger.register('service_state', ServiceStateAlertLogger)
alert_logger.register('resource_state', ResourceStateAlertLogger)
alert_logger.register('customer_state', CustomerStateAlertLogger)
alert_logger.register('quota_check', QuotaCheckAlertLogger)
