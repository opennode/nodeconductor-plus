from __future__ import unicode_literals

from django.db import models

from nodeconductor.structure import models as structure_models


class DigitalOceanService(structure_models.Service):
    auth_token = models.CharField(max_length=64)
    projects = models.ManyToManyField(
        structure_models.Project, related_name='services', through='DigitalOceanServiceProjectLink')

    def get_backend(self, sp_link=None):
        from .backend import DigitalOceanBackend
        return DigitalOceanBackend(self)


class DigitalOceanServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(DigitalOceanService)


class Region(structure_models.ServiceProperty):
    service = models.ForeignKey(DigitalOceanService, related_name='regions')


class Image(structure_models.ServiceProperty):
    service = models.ForeignKey(DigitalOceanService, related_name='images')
    regions = models.ManyToManyField(Region)


class Size(structure_models.ServiceProperty):
    service = models.ForeignKey(DigitalOceanService, related_name='sizes')
    regions = models.ManyToManyField(Region)

    cores = models.PositiveSmallIntegerField(help_text='Number of cores in a VM')
    ram = models.PositiveIntegerField(help_text='Memory size in MiB')
    disk = models.PositiveIntegerField(help_text='Disk size in MiB')
    bandwidth = models.PositiveIntegerField(help_text='Bandwidth size in MiB')


class Droplet(structure_models.Resource, structure_models.VirtualMachineMixin):
    service_project_link = models.ForeignKey(
        DigitalOceanServiceProjectLink, related_name='resources', on_delete=models.PROTECT)
