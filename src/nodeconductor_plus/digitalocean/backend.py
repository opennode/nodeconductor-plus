from __future__ import unicode_literals

import logging
import digitalocean

from django.db import transaction

from nodeconductor.core.tasks import send_task
from nodeconductor.core.models import SshPublicKey
from nodeconductor.iaas.backend import ServiceBackend

from . import models


logger = logging.getLogger(__name__)


class DigitalOceanBackend(object):

    def __init__(self, settings):
        backend_class = DigitalOceanDummyBackend if settings.dummy else DigitalOceanRealBackend
        self.backend = backend_class(settings)

    def __getattr__(self, name):
        return getattr(self.backend, name)


class DigitalOceanBaseBackend(ServiceBackend):

    def __init__(self, settings):
        self.settings = settings
        self.manager = digitalocean.Manager(token=settings.token)

    def sync(self):
        self.pull_service_properties()

    def provision(self, droplet, region=None, image=None, size=None, ssh_key=None):
        send_task('digitalocean', 'provision')(
            droplet.uuid.hex,
            backend_region_id=region.backend_id,
            backend_image_id=image.backend_id,
            backend_size_id=size.backend_id,
            ssh_key_uuid=ssh_key.uuid.hex if ssh_key else None)

    def destroy(self, droplet):
        self.delete_droplet(droplet)

    def start(self, droplet):
        droplet.schedule_starting()
        droplet.save()
        send_task('digitalocean', 'start')(droplet.uuid.hex)

    def stop(self, droplet):
        droplet.schedule_stopping()
        droplet.save()
        send_task('digitalocean', 'stop')(droplet.uuid.hex)

    def restart(self, droplet):
        droplet.schedule_restarting()
        droplet.save()
        send_task('digitalocean', 'restart')(droplet.uuid.hex)


class DigitalOceanRealBackend(DigitalOceanBaseBackend):
    """ NodeConductor interface to Digital Ocean API.
        https://developers.digitalocean.com/documentation/v2/
    """

    def pull_service_properties(self):
        self.pull_regions()
        self.pull_images()
        self.pull_sizes()

    def pull_regions(self):
        for backend_region in self.manager.get_all_regions():
            models.Region.objects.update_or_create(
                settings=self.settings,
                backend_id=backend_region.slug,
                defaults={'name': backend_region.name})

    def pull_images(self):
        for backend_image in self.manager.get_all_images():
            with transaction.atomic():
                image, _ = models.Image.objects.update_or_create(
                    settings=self.settings,
                    backend_id=backend_image.id,
                    defaults={'name': backend_image.name})
                self._update_entity_regions(image, backend_image)

    def pull_sizes(self):
        for backend_size in self.manager.get_all_sizes():
            with transaction.atomic():
                size, _ = models.Size.objects.update_or_create(
                    settings=self.settings,
                    backend_id=backend_size.slug,
                    defaults={
                        'name': backend_size.slug,
                        'cores': backend_size.vcpus,
                        'ram': backend_size.memory,
                        'disk': self.gb2mb(backend_size.disk),
                        'transfer': int(self.tb2mb(backend_size.transfer))})
                self._update_entity_regions(size, backend_size)

    def provision_droplet(self, droplet, backend_region_id=None, backend_image_id=None,
                          backend_size_id=None, ssh_key_uuid=None):
        if ssh_key_uuid:
            ssh_key = SshPublicKey.object.get(uuid=ssh_key_uuid)
            backend_ssh_key = self.add_ssh_key(ssh_key)

        backend_droplet = digitalocean.Droplet(
            token=self.manager.token,
            name=droplet.name,
            user_data=droplet.user_data,
            region=backend_region_id,
            image=backend_image_id,
            size_slug=backend_size_id,
            ssh_keys=[backend_ssh_key.id] if ssh_key_uuid else [])

        backend_droplet.create()

        if ssh_key_uuid:
            droplet.key_name = ssh_key.name
            droplet.key_fingerprint = ssh_key.fingerprint

        droplet.backend_id = backend_droplet.id
        droplet.cores = backend_droplet.vcpus
        droplet.ram = backend_droplet.memory
        droplet.disk = self.gb2mb(backend_droplet.disk)
        # XXX: disabled as library doesn't contain this attribute
        # droplet.transfer = int(self.tb2mb(backend_droplet.transfer))
        droplet.save()

    def delete_droplet(self, droplet):
        backend_droplet = self.manager.get_droplet(droplet.backend_id)
        backend_droplet.destroy()

    def add_ssh_key(self, ssh_key):
        backend_ssh_key = digitalocean.SSHKey(
            token=self.manager.token,
            name=ssh_key.name,
            public_key=ssh_key.public_key)

        backend_ssh_key.create()
        return backend_ssh_key

    def remove_ssh_key(self, ssh_key):
        backend_ssh_key = digitalocean.SSHKey(
            token=self.manager.token,
            fingerprint=ssh_key.fingerprint)

        backend_ssh_key.load()
        backend_ssh_key.destroy()

    def _update_entity_regions(self, entity, backend_entity):
        all_regions = set(entity.regions.all())
        actual_regions = set(models.Region.objects.filter(
            settings=self.settings, backend_id__in=backend_entity.regions))

        entity.regions.add(*(actual_regions - all_regions))
        entity.regions.remove(*(all_regions - actual_regions))


class DigitalOceanDummyBackend(DigitalOceanBaseBackend):
    pass
