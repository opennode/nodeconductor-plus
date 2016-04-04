from nodeconductor.logging.loggers import AlertLogger, alert_logger


class DigitalOceanAlertLogger(AlertLogger):
    settings = 'structure.ServiceSettings'

    class Meta:
        alert_types = ['token_is_read_only']


alert_logger.register('digital_ocean', DigitalOceanAlertLogger)
