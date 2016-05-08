from __future__ import unicode_literals

from django.db import models

from nodeconductor.core import models as core_models
from nodeconductor.quotas import models as quotas_models
from nodeconductor.structure import models as structure_models


class GitLabService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='gitlab_services', through='GitLabServiceProjectLink')

    class Meta(structure_models.Service.Meta):
        verbose_name = 'GitLab service'
        verbose_name_plural = 'GitLab service'


class GitLabServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(GitLabService)

    class Meta(structure_models.ServiceProjectLink.Meta):
        verbose_name = 'GitLab service project link'
        verbose_name_plural = 'GitLab service project link'


class GitLabResource(structure_models.Resource, core_models.SerializableAbstractMixin):
    class Meta(object):
        abstract = True

    def get_related_users(self):
        return self.service_project_link.project.get_users()


class Group(GitLabResource):
    path = models.CharField(max_length=100, blank=True)
    service_project_link = models.ForeignKey(
        GitLabServiceProjectLink, related_name='groups', on_delete=models.PROTECT)

    @property
    def web_url(self):
        return "{}groups/{}".format(
            self.service_project_link.service.settings.backend_url,
            self.path) if self.path else None

    # a generic URL for access to the resource
    def get_access_url(self):
        return self.web_url


class Project(quotas_models.QuotaModelMixin, GitLabResource):
    class Levels:
        PRIVATE = 0
        INTERNAL = 10
        PUBLIC = 20

        CHOICES = (
            (PRIVATE, 'Project access must be granted explicitly for each user.'),
            (INTERNAL, 'The project can be cloned by any logged in user.'),
            (PUBLIC, 'The project can be cloned without any authentication.'),
        )

    QUOTAS_NAMES = ['commit_count']  # XXX: commit_count quotas is used only for statistics

    service_project_link = models.ForeignKey(
        GitLabServiceProjectLink, related_name='projects', on_delete=models.PROTECT)

    group = models.ForeignKey(Group, related_name='projects')
    visibility_level = models.SmallIntegerField(choices=Levels.CHOICES)
    http_url_to_repo = models.CharField(max_length=255, blank=True)
    ssh_url_to_repo = models.CharField(max_length=255, blank=True)
    web_url = models.CharField(max_length=255, blank=True)

    def get_related_users(self):
        return self.service_project_link.project.get_users()

    # a generic URL for access to the resource
    def get_access_url(self):
        return self.web_url
