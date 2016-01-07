from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models import signals
from django.conf import settings

from . import handlers


class NodeConductorAuthConfig(AppConfig):
    name = 'nodeconductor_plus.nodeconductor_auth'
    verbose_name = "NodeConductorPlus Auth"

    # See, https://docs.djangoproject.com/en/1.7/ref/applications/#django.apps.AppConfig.ready
    def ready(self):
        signals.post_save.connect(
            handlers.create_auth_profile,
            sender=settings.AUTH_USER_MODEL,
            dispatch_uid='nodeconductor_plus.nodeconductor_auth.handlers.create_auth_profile',
        )
