from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from nodeconductor.structure import models as structure_models


class DigitalOceanService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='digitalocean_services', through='DigitalOceanServiceProjectLink')


class DigitalOceanServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(DigitalOceanService)


class Region(structure_models.GeneralServiceProperty):
    pass


@python_2_unicode_compatible
class Image(structure_models.GeneralServiceProperty):
    regions = models.ManyToManyField(Region)
    distribution = models.CharField(max_length=100)
    type = models.CharField(max_length=100)

    @property
    def is_ssh_key_mandatory(self):
        OPTIONAL = 'Fedora', 'CentOS', 'Debian'
        MANDATORY = 'Ubuntu', 'FreeBSD', 'CoreOS'
        return self.distribution in MANDATORY

    def __str__(self):
        return '{} {} ({})'.format(self.name, self.distribution, self.type)


class Size(structure_models.GeneralServiceProperty):
    regions = models.ManyToManyField(Region)

    cores = models.PositiveSmallIntegerField(help_text='Number of cores in a VM')
    ram = models.PositiveIntegerField(help_text='Memory size in MiB')
    disk = models.PositiveIntegerField(help_text='Disk size in MiB')
    transfer = models.PositiveIntegerField(help_text='Amount of transfer bandwidth in MiB')
    price = models.PositiveIntegerField(help_text='Hourly price in USD')


class Droplet(structure_models.VirtualMachineMixin, structure_models.Resource):
    service_project_link = models.ForeignKey(
        DigitalOceanServiceProjectLink, related_name='droplets', on_delete=models.PROTECT)

    transfer = models.PositiveIntegerField(default=0, help_text='Amount of transfer bandwidth in MiB')
