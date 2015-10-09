from django.apps import AppConfig
from django.db.models import signals

from . import handlers
from nodeconductor.quotas import handlers as quotas_handlers
from nodeconductor.structure import SupportedServices


class GitLabConfig(AppConfig):
    name = 'nodeconductor_plus.gitlab'
    verbose_name = "NodeConductor GitLab"

    def ready(self):
        GitLabService = self.get_model('GitLabService')
        GitLabServiceProjectLink = self.get_model('GitLabServiceProjectLink')
        Project = self.get_model('Project')

        from .backend import GitLabBackend
        SupportedServices.register_backend(GitLabService, GitLabBackend)

        signals.post_save.connect(
            handlers.sync_service_project_link,
            sender=GitLabServiceProjectLink,
            dispatch_uid='nodeconductor_plus.gitlab.handlers.sync_service_project_link',
        )

        signals.post_save.connect(
            quotas_handlers.add_quotas_to_scope,
            sender=Project,
            dispatch_uid='nodeconductor_plus.gitlab.handlers.add_quotas_to_project',
        )
