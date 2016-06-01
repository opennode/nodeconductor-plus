from .log import alert_logger


def open_token_scope_alert(service_project_link):
    settings = service_project_link.service.settings

    settings.set_erred()
    settings.error_message = 'Token is read-only.'
    settings.save(update_fields=['state', 'error_message'])

    alert_logger.digital_ocean.warning(
        'DigitalOcean token for {settings_name} is read-only.',
        scope=settings,
        alert_type='token_is_read_only',
        alert_context={'settings': settings})


def close_token_scope_alert(service_project_link):
    settings = service_project_link.service.settings
    alert_logger.digital_ocean.close(scope=settings, alert_type='token_is_read_only')
