import urlparse

from django.db import models

from nodeconductor.structure import models as structure_models


class GitLabService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='gitlab_services', through='GitLabServiceProjectLink')


class GitLabServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(GitLabService)


class Group(structure_models.Resource):
    path = models.CharField(max_length=100)
    service_project_link = models.ForeignKey(
        GitLabServiceProjectLink, related_name='groups', on_delete=models.PROTECT)

    @property
    def backend_url(self):
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
        GitLabServiceProjectLink, related_name='projects', on_delete=models.PROTECT)

    visibility_level = models.SmallIntegerField(choices=Levels.CHOICES)
    path = models.CharField(max_length=100)

    @property
    def backend_url(self):
        if not self.path:
            return None
        url = self.service_project_link.service.settings.backend_url
        if not url.endswith('/'):
            url += '/'
        return "{}{}".format(url, self.path)

    @property
    def http_url_to_repo(self):
        if not self.path:
            return None
        url = self.service_project_link.service.settings.backend_url
        if not url.endswith('/'):
            url += '/'
        return "{}{}.git".format(url, self.path)

    @property
    def ssh_url_to_repo(self):
        if not self.path:
            return None
        url_parts = urlparse.urlparse(self.service_project_link.service.settings.backend_url)
        return "git@{}:{}.git".format(url_parts.hostname, self.path)
