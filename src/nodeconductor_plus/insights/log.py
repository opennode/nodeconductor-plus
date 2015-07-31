from nodeconductor.logging.log import AlertLogger, alert_logger
from nodeconductor.structure.models import Service


class ResourceImportAlertLogger(AlertLogger):
    service = Service

    class Meta:
        alert_types = ('service_has_unmanaged_resources', )


alert_logger.register('resource_import', ResourceImportAlertLogger)
