from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

from nodeconductor.core.models import RuntimeStateMixin, StateMixin
from nodeconductor.cost_tracking.models import PayableMixin
from nodeconductor.structure import models as structure_models


from .log import alert_logger


class DigitalOceanService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='digitalocean_services', through='DigitalOceanServiceProjectLink')

    class Meta(structure_models.Service.Meta):
        verbose_name = 'DigitalOcean service'
        verbose_name_plural = 'DigitalOcean services'

    def raise_readonly_token_alert(self):
        """ Raise alert if provided token is read-only """
        alert_logger.digital_ocean.warning(
            'DigitalOcean token for {settings_name} is read-only.',
            scope=self.settings,
            alert_type='token_is_read_only',
            alert_context={'settings': self.settings})

    def close_readonly_token_alert(self):
        alert_logger.digital_ocean.close(scope=self.settings, alert_type='token_is_read_only')


class DigitalOceanServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(DigitalOceanService)

    class Meta(structure_models.ServiceProjectLink.Meta):
        verbose_name = 'DigitalOcean service project link'
        verbose_name_plural = 'DigitalOcean service project links'


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
    price = models.DecimalField('Hourly price rate', default=0, max_digits=11, decimal_places=5)


class Droplet(RuntimeStateMixin, StateMixin, PayableMixin,
              structure_models.VirtualMachineMixin, structure_models.ResourceMixin):
    service_project_link = models.ForeignKey(
        DigitalOceanServiceProjectLink, related_name='droplets', on_delete=models.PROTECT)

    transfer = models.PositiveIntegerField(default=0, help_text='Amount of transfer bandwidth in MiB')
