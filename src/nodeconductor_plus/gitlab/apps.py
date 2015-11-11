from django.apps import AppConfig

from nodeconductor.structure import SupportedServices


class GitLabConfig(AppConfig):
    name = 'nodeconductor_plus.gitlab'
    verbose_name = "NodeConductor GitLab"

    def ready(self):
        Service = self.get_model('Service')

        from .backend import GitLabBackend
        SupportedServices.register_backend(Service, GitLabBackend)
