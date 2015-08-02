from django.apps import AppConfig
from django.db.models import signals

from nodeconductor.structure.models import Service
from nodeconductor_plus.insights import handlers


class InsightsConfig(AppConfig):
    name = 'nodeconductor_plus.insights'
    verbose_name = 'NodeConductor Insights'

    def ready(self):
        for model in Service.get_all_models():
            signals.post_save.connect(
                handlers.check_unmanaged_resources,
                sender=model
            )
