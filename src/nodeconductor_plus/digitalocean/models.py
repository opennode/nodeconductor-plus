from __future__ import unicode_literals

from django.db import models

from nodeconductor.structure import models as structure_models


class DigitalOceanService(structure_models.Service):
    auth_token = models.CharField(max_length=64)
    projects = models.ManyToManyField(
        structure_models.Project, related_name='services', through='DigitalOceanServiceProjectLink')

    def get_backend(self):
        from .backend import DigitalOceanBackend
        return DigitalOceanBackend(self)


class DigitalOceanServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(DigitalOceanService)


class Region(structure_models.Resource):
    service = models.ForeignKey(DigitalOceanService, related_name='regions')


class Image(structure_models.Resource):
    service = models.ForeignKey(DigitalOceanService, related_name='images')
    regions = models.ManyToManyField(Region)
