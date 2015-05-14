from __future__ import unicode_literals

import logging
import digitalocean


logger = logging.getLogger(__name__)


class ServiceBackend(object):
    """ Basic service backed with only common methods pre-defined. """
    # TODO: Move it somewhere else or deprecate
    def sync(self):
        raise NotImplementedError


class DigitalOceanBackend(object):

    def __init__(self, service):
        backend_class = DigitalOceanDummyBackend if service.dummy else DigitalOceanRealBackend
        self.backend = backend_class(service)

    def __getattr__(self, name):
        return getattr(self.backend, name)


class DigitalOceanBaseBackend(ServiceBackend):

    def __init__(self, service):
        self.service = service
        self.manager = digitalocean.Manager(token=service.auth_token)

    def sync(self):
        self.pull_resources()


class DigitalOceanRealBackend(DigitalOceanBaseBackend):

    def pull_resources(self):
        self.pull_regions()
        self.pull_images()

    def pull_regions(self):
        for do_region in self.manager.get_all_regions():
            self.service.regions.update_or_create(
                backend_id=do_region.slug, defaults={'name': do_region.name})

    def pull_images(self):
        for do_image in self.manager.get_all_images():
            nc_image, _ = self.service.images.update_or_create(
                backend_id=do_image.id, defaults={'name': do_image.name})

            nc_regions = set(nc_image.regions.all())
            bk_regions = set(self.service.regions.filter(backend_id__in=do_image.regions))

            nc_image.regions.add(*(bk_regions - nc_regions))
            nc_image.regions.remove(*(nc_regions - bk_regions))


class DigitalOceanDummyBackend(DigitalOceanBaseBackend):
    pass
