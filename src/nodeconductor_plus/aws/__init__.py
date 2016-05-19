default_app_config = 'nodeconductor_plus.aws.apps.AWSConfig'


class ResourceType(object):
    INSTANCE = 'instance'
    VOLUME = 'volume'

    CHOICES = (
        (INSTANCE, 'Instance'),
        (VOLUME, 'Volume'),
    )
