from __future__ import unicode_literals

import logging
import digitalocean

from django.db import IntegrityError, transaction
from django.utils import six

from nodeconductor.core.tasks import send_task
from nodeconductor.core.models import SshPublicKey
from nodeconductor.structure import ServiceBackend, ServiceBackendError

from . import models


logger = logging.getLogger(__name__)


class DigitalOceanBackendError(ServiceBackendError):
    pass


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
        self.pull_droplets()

    def provision(self, droplet, region=None, image=None, size=None, ssh_key=None):
        droplet.cores = size.cores
        droplet.ram = size.ram
        droplet.disk = size.disk
        droplet.transfer = size.transfer
        droplet.save()

        send_task('digitalocean', 'provision')(
            droplet.uuid.hex,
            backend_region_id=region.backend_id,
            backend_image_id=image.backend_id,
            backend_size_id=size.backend_id,
            ssh_key_uuid=ssh_key.uuid.hex if ssh_key else None)

    def destroy(self, droplet):
        droplet.schedule_deletion()
        droplet.save()
        send_task('digitalocean', 'destroy')(droplet.uuid.hex)

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

    def add_ssh_key(self, ssh_key, service_project_link=None):
        try:
            self.push_ssh_key(ssh_key)
        except digitalocean.DataReadError as e:
            logger.exception('Failed to propagate ssh public key %s to backend', ssh_key.name)
            six.reraise(DigitalOceanBackendError, e)

    def remove_ssh_key(self, ssh_key, service_project_link=None):
        try:
            backend_ssh_key = self.pull_ssh_key(ssh_key)
            backend_ssh_key.destroy()
        except digitalocean.DataReadError as e:
            logger.exception('Failed to delete ssh public key %s from backend', ssh_key.name)
            six.reraise(DigitalOceanBackendError, e)


class DigitalOceanRealBackend(DigitalOceanBaseBackend):
    """ NodeConductor interface to Digital Ocean API.
        https://developers.digitalocean.com/documentation/v2/
        https://github.com/koalalorenzo/python-digitalocean
    """

    def ping(self):
        tries_count = 3
        for _ in range(tries_count):
            try:
                self.manager.get_account()
            except digitalocean.DataReadError:
                pass
            else:
                return True
        return False

    def ping_resource(self, droplet):
        tries_count = 3
        for _ in range(tries_count):
            try:
                self.get_droplet(droplet.backend_id)
            except DigitalOceanBackendError:
                logger.warning('Droplet %s (UUID: %s) is unreachable' % (droplet.name, droplet.uuid.hex))
            else:
                return True
        return False

    def pull_service_properties(self):
        self.pull_regions()
        self.pull_images()
        self.pull_sizes()

    @transaction.atomic
    def pull_regions(self):
        cur_regions = self._get_current_properties(models.Region)
        for backend_region in self.manager.get_all_regions():
            if backend_region.available:
                cur_regions.pop(backend_region.slug, None)
                try:
                    models.Region.objects.update_or_create(
                        backend_id=backend_region.slug,
                        defaults={'name': backend_region.name})
                except IntegrityError:
                    logger.warning(
                        'Could not create DigitalOcean region with id %s due to concurrent update',
                        backend_region.slug)

        map(lambda i: i.delete(), cur_regions.values())

    @transaction.atomic
    def pull_images(self):
        cur_images = self._get_current_properties(models.Image)
        for backend_image in self.manager.get_all_images():
            cur_images.pop(str(backend_image.id), None)
            try:
                image, _ = models.Image.objects.update_or_create(
                    backend_id=backend_image.id,
                    defaults={
                        'name': backend_image.name,
                        'type': backend_image.type,
                        'distribution': backend_image.distribution,
                    })
                self._update_entity_regions(image, backend_image)
            except IntegrityError:
                logger.warning(
                    'Could not create DigitalOcean image with id %s due to concurrent update',
                    backend_image.id)

        map(lambda i: i.delete(), cur_images.values())

    @transaction.atomic
    def pull_sizes(self):
        cur_sizes = self._get_current_properties(models.Size)
        for backend_size in self.manager.get_all_sizes():
            cur_sizes.pop(backend_size.slug, None)
            try:
                size, _ = models.Size.objects.update_or_create(
                    backend_id=backend_size.slug,
                    defaults={
                        'name': backend_size.slug,
                        'cores': backend_size.vcpus,
                        'ram': backend_size.memory,
                        'disk': self.gb2mb(backend_size.disk),
                        'transfer': int(self.tb2mb(backend_size.transfer))})
                self._update_entity_regions(size, backend_size)
            except IntegrityError:
                logger.warning(
                    'Could not create DigitalOcean size with id %s due to concurrent update',
                    backend_size.slug)

        map(lambda i: i.delete(), cur_sizes.values())

    @transaction.atomic
    def pull_droplets(self):
        backend_droplets = {six.text_type(droplet.id): droplet for droplet in self.get_all_droplets()}
        backend_ids = set(backend_droplets.keys())

        nc_droplets = models.Droplet.objects.filter(service_project_link__service__settings=self.settings)
        nc_droplets = {droplet.backend_id: droplet for droplet in nc_droplets}
        nc_ids = set(nc_droplets.keys())

        # Mark stale droplets as erred if they are removed from the backend
        for droplet_id in nc_ids - backend_ids:
            nc_droplet = nc_droplets[droplet_id]
            nc_droplet.set_erred()
            nc_droplet.save()

        # Update state of matching droplets
        for droplet_id in nc_ids & backend_ids:
            backend_droplet = backend_droplets[droplet_id]
            nc_droplet = nc_droplets[droplet_id]
            nc_droplet.state = self._get_droplet_state(backend_droplet)
            nc_droplet.save()

    def _get_droplet_state(self, droplet):
        digitalocean_to_nodeconductor = {
            'new': models.Droplet.States.PROVISIONING,
            'active': models.Droplet.States.ONLINE,
            'off': models.Droplet.States.OFFLINE,
            'archive': models.Droplet.States.OFFLINE,
        }

        return digitalocean_to_nodeconductor.get(droplet.status, models.Droplet.States.ERRED)

    def provision_droplet(self, droplet, backend_region_id=None, backend_image_id=None,
                          backend_size_id=None, ssh_key_uuid=None):
        if ssh_key_uuid:
            ssh_key = SshPublicKey.objects.get(uuid=ssh_key_uuid)
            backend_ssh_key = self.get_or_create_ssh_key(ssh_key)

        try:
            backend_droplet = digitalocean.Droplet(
                token=self.manager.token,
                name=droplet.name,
                user_data=droplet.user_data,
                region=backend_region_id,
                image=backend_image_id,
                size_slug=backend_size_id,
                ssh_keys=[backend_ssh_key.id] if ssh_key_uuid else [])
            backend_droplet.create()
        except digitalocean.DataReadError as e:
            logger.exception('Failed to provision droplet %s', droplet.name)
            six.reraise(DigitalOceanBackendError, e)

        if ssh_key_uuid:
            droplet.key_name = ssh_key.name
            droplet.key_fingerprint = ssh_key.fingerprint

        droplet.backend_id = backend_droplet.id
        droplet.ip_address = backend_droplet.ip_address
        droplet.save()
        return backend_droplet

    def get_droplet(self, backend_droplet_id):
        try:
            return self.manager.get_droplet(backend_droplet_id)
        except digitalocean.DataReadError as e:
            six.reraise(DigitalOceanBackendError, e)

    def get_monthly_cost_estimate(self, droplet):
        backend_droplet = self.get_droplet(droplet.backend_id)
        return backend_droplet.size['price_monthly']

    def get_resources_for_import(self):
        cur_droplets = models.Droplet.objects.all().values_list('backend_id', flat=True)
        statuses = ('active', 'off')
        droplets = self.get_all_droplets()
        return [{
            'id': droplet.id,
            'name': droplet.name,
            'created_at': droplet.created_at,
            'kernel': droplet.kernel['name'],
            'cores': droplet.vcpus,
            'ram': droplet.memory,
            'disk': self.gb2mb(droplet.disk),
        } for droplet in droplets
            if str(droplet.id) not in cur_droplets and droplet.status in statuses]

    def get_imported_resources(self):
        try:
            ids = [droplet.id for droplet in self.get_all_droplets()]
            return models.Droplet.objects.filter(backend_id__in=ids)
        except DigitalOceanBackendError:
            return []

    def get_all_droplets(self):
        try:
            return self.manager.get_all_droplets()
        except digitalocean.Error as e:
            six.reraise(DigitalOceanBackendError, e)

    def get_or_create_ssh_key(self, ssh_key):
        try:
            backend_ssh_key = self.push_ssh_key(ssh_key)
        except digitalocean.DataReadError:
            backend_ssh_key = self.pull_ssh_key(ssh_key)
        return backend_ssh_key

    def push_ssh_key(self, ssh_key):
        backend_ssh_key = digitalocean.SSHKey(
            token=self.manager.token,
            name=ssh_key.name,
            public_key=ssh_key.public_key)

        backend_ssh_key.create()
        return backend_ssh_key

    def pull_ssh_key(self, ssh_key):
        backend_ssh_key = digitalocean.SSHKey(
            token=self.manager.token,
            fingerprint=ssh_key.fingerprint,
            id=None)

        backend_ssh_key.load()
        return backend_ssh_key

    def _get_current_properties(self, model):
        return {p.backend_id: p for p in model.objects.all()}

    def _update_entity_regions(self, entity, backend_entity):
        all_regions = set(entity.regions.all())
        actual_regions = set(models.Region.objects.filter(backend_id__in=backend_entity.regions))

        entity.regions.add(*(actual_regions - all_regions))
        entity.regions.remove(*(all_regions - actual_regions))


class DigitalOceanDummyBackend(DigitalOceanBaseBackend):
    pass
