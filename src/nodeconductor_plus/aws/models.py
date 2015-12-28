from django.db import models

from nodeconductor.structure import models as structure_models


class AWSService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='aws_services', through='AWSServiceProjectLink')


class AWSServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(AWSService)


class Region(structure_models.GeneralServiceProperty):
    class Meta:
        ordering = ['name']


class Image(structure_models.GeneralServiceProperty):
    class Meta:
        ordering = ['name']

    region = models.ForeignKey(Region)


class Size(structure_models.GeneralServiceProperty):
    class Meta:
        ordering = ['name']

    regions = models.ManyToManyField(Region)
    cores = models.PositiveSmallIntegerField(help_text='Number of cores in a VM')
    ram = models.PositiveIntegerField(help_text='Memory size in MiB')
    disk = models.PositiveIntegerField(help_text='Disk size in MiB')


class Instance(structure_models.VirtualMachineMixin, structure_models.Resource):
    service_project_link = models.ForeignKey(
        AWSServiceProjectLink, related_name='instances', on_delete=models.PROTECT)

    region = models.ForeignKey(Region)
    external_ips = models.GenericIPAddressField(null=True, blank=True, protocol='IPv4')
    internal_ips = models.GenericIPAddressField(null=True, blank=True, protocol='IPv4')

    def get_backend(self):
        return super(Instance, self).get_backend(region=self.region.backend_id)
