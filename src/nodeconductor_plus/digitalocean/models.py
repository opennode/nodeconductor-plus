from __future__ import unicode_literals

from django.db import models

from nodeconductor.structure import models as structure_models
from nodeconductor.iaas import models as iaas_models


class DigitalOceanService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='digitalocean_services',
        through='DigitalOceanServiceProjectLink')


class DigitalOceanServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(DigitalOceanService)


class Region(structure_models.ServiceProperty):
    pass


class Image(structure_models.ServiceProperty):
    regions = models.ManyToManyField(Region)


class Size(structure_models.ServiceProperty):
    regions = models.ManyToManyField(Region)

    cores = models.PositiveSmallIntegerField(help_text='Number of cores in a VM')
    ram = models.PositiveIntegerField(help_text='Memory size in MiB')
    disk = models.PositiveIntegerField(help_text='Disk size in MiB')
    transfer = models.PositiveIntegerField(help_text='Amount of transfer bandwidth in MiB')


class Droplet(structure_models.Resource, iaas_models.VirtualMachineMixin):
    service_project_link = models.ForeignKey(
        DigitalOceanServiceProjectLink, related_name='droplets', on_delete=models.PROTECT)

    cores = models.PositiveSmallIntegerField(default=0, help_text='Number of cores in a VM')
    ram = models.PositiveIntegerField(default=0, help_text='Memory size in MiB')
    disk = models.PositiveIntegerField(default=0, help_text='Disk size in MiB')
    transfer = models.PositiveIntegerField(default=0, help_text='Amount of transfer bandwidth in MiB')
