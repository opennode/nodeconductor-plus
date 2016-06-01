from django.apps import AppConfig
from django.db.models import signals


class GitLabConfig(AppConfig):
    name = 'nodeconductor_plus.gitlab'
    verbose_name = "NodeConductor GitLab"
    service_name = 'GitLab'

    def ready(self):
        from nodeconductor.quotas import handlers as quotas_handlers
        from nodeconductor.structure import SupportedServices

        Project = self.get_model('Project')

        from .backend import GitLabBackend
        SupportedServices.register_backend(GitLabBackend)

        signals.post_save.connect(
            quotas_handlers.add_quotas_to_scope,
            sender=Project,
            dispatch_uid='nodeconductor_plus.gitlab.handlers.add_quotas_to_project',
        )
