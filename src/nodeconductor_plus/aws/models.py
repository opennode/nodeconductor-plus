from django.db import models

from nodeconductor.structure import models as structure_models


class Service(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='+', through='ServiceProjectLink')


class ServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(Service)


class Image(structure_models.ServiceProperty):
    pass


class Instance(structure_models.VirtualMachineMixin, structure_models.Resource):
    service_project_link = models.ForeignKey(
        ServiceProjectLink, related_name='instances', on_delete=models.PROTECT)

    external_ips = models.GenericIPAddressField(null=True, blank=True, protocol='IPv4')
    internal_ips = models.GenericIPAddressField(null=True, blank=True, protocol='IPv4')
