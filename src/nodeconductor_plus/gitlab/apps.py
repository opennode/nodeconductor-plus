from django.apps import AppConfig

from nodeconductor.structure import SupportedServices


class GitLabConfig(AppConfig):
    name = 'nodeconductor_plus.gitlab'
    verbose_name = "NodeConductor GitLab"

    def ready(self):
        GitLabService = self.get_model('GitLabService')

        from .backend import GitLabBackend
        SupportedServices.register_backend(GitLabService, GitLabBackend)
