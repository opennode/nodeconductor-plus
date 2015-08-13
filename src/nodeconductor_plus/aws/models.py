from django.db import models

from nodeconductor.structure import models as structure_models


class AWSService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='aws_services', through='AWSServiceProjectLink')


class AWSServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(AWSService)


class Image(structure_models.ServiceProperty):
    pass


class Instance(structure_models.VirtualMachineMixin, structure_models.Resource):
    service_project_link = models.ForeignKey(
        AWSServiceProjectLink, related_name='instances', on_delete=models.PROTECT)

    external_ips = models.GenericIPAddressField(null=True, blank=True, protocol='IPv4')
    internal_ips = models.GenericIPAddressField(null=True, blank=True, protocol='IPv4')
