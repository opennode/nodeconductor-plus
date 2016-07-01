from nodeconductor.core import models as core_models, utils as core_utils

from . import models, tasks


def remove_ssh_keys_from_service(sender, structure, user, role, **kwargs):
    """ Remove user ssh keys If he doesn't have access to service anymore. """
    services = models.DigitalOceanService.objects.filter(**{sender.__name__.lower(): structure})
    services = services.exclude(customer__roles__permission_group__user=user)
    services = services.exclude(customer__projects__roles__permission_group__user=user)
    keys = core_models.SshPublicKey.objects.filter(user=user)
    for service in services:
        serialized_service = core_utils.serialize_instance(service)
        for key in keys:
            serialized_key = core_utils.serialize_instance(key)
            tasks.RemoveSshKeyTask().delay(serialized_key, serialized_service)
