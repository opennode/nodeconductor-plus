from .log import alert_logger


def log_read_only_token_alert(sender, instance, **kwargs):
    if instance.error_message == 'You do not have access for the attempted action.':
        settings = instance.service_project_link.service.settings

        settings.set_erred()
        settings.error_message = instance.error_message
        settings.save(update_fields=['state', 'error_message'])

        alert_logger.digital_ocean_token.warning(
            'DigitalOcean token for {settings_name} is read-only.',
            scope=settings,
            alert_type='token_is_read_only',
            alert_context={'settings': settings})
