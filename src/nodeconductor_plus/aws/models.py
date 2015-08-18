from django.db import models

from nodeconductor.structure import models as structure_models


class AWSService(structure_models.Service):
    Regions = (('us-east-1', 'US East (N. Virginia)'),
               ('us-west-2', 'US West (Oregon)'),
               ('us-west-1', 'US West (N. California)'),
               ('eu-west-1', 'EU (Ireland)'),
               ('eu-central-1 ', 'EU (Frankfurt)'),
               ('ap-southeast-1', 'Asia Pacific (Singapore)'),
               ('ap-southeast-2', 'Asia Pacific (Sydney)'),
               ('ap-northeast-1', 'Asia Pacific (Tokyo)'),
               ('sa-east-1', 'South America (Sao Paulo)'))

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
