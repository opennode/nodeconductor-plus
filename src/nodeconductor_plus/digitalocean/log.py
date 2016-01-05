from nodeconductor.logging.log import AlertLogger, alert_logger


class DigitalOceanTokenAlertLogger(AlertLogger):
    settings = 'structure.ServiceSettings'

    class Meta:
        alert_types = ['token_is_read_only']


alert_logger.register('digital_ocean_token', DigitalOceanTokenAlertLogger)
