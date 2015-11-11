from django.db import models

from nodeconductor.structure import models as structure_models


class Service(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='+', through='ServiceProjectLink')


class ServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(Service)


class Group(structure_models.Resource):
    path = models.CharField(max_length=100, blank=True)
    service_project_link = models.ForeignKey(
        ServiceProjectLink, related_name='groups', on_delete=models.PROTECT)

    @property
    def web_url(self):
        return "{}groups/{}".format(
            self.service_project_link.service.settings.backend_url,
            self.path) if self.path else None


class Project(structure_models.Resource):
    class Levels:
        PRIVATE = 0
        INTERNAL = 10
        PUBLIC = 20

        CHOICES = (
            (PRIVATE, 'Project access must be granted explicitly for each user.'),
            (INTERNAL, 'The project can be cloned by any logged in user.'),
            (PUBLIC, 'The project can be cloned without any authentication.'),
        )

    service_project_link = models.ForeignKey(
        ServiceProjectLink, related_name='projects', on_delete=models.PROTECT)

    group = models.ForeignKey(Group, related_name='projects', blank=True, null=True)
    visibility_level = models.SmallIntegerField(choices=Levels.CHOICES)
    http_url_to_repo = models.CharField(max_length=255, blank=True)
    ssh_url_to_repo = models.CharField(max_length=255, blank=True)
    web_url = models.CharField(max_length=255, blank=True)
