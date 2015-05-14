from __future__ import unicode_literals

from django.db import models

from nodeconductor.structure import models as structure_models


class DigitalOceanService(structure_models.Service):
    projects = 'DigitalOceanProjectLink'
    auth_token = models.CharField(max_length=64)

    def get_backend(self):
        from .backend import DigitalOceanBackend
        return DigitalOceanBackend(self)


class DigitalOceanProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(DigitalOceanService)


class Region(structure_models.ServiceResource):
    service = models.ForeignKey(DigitalOceanService, related_name='regions')


class Image(structure_models.ServiceResource):
    service = models.ForeignKey(DigitalOceanService, related_name='images')
    regions = models.ManyToManyField(Region)
