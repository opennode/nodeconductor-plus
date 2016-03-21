from nodeconductor.core import NodeConductorExtension


class AuthExtension(NodeConductorExtension):

    class Settings:
        # XXX: Split these settings across corresponding NCPlus apps
        NODECONDUCTOR_PLUS = {
            'GOOGLE_SECRET': 'CHANGE_ME_TO_GOOGLE_SECRET',
            'FACEBOOK_SECRET': 'CHANGE_ME_TO_FACEBOOK_SECRET',
            'PROJECTED_COSTS_EXCESS': 20,
            'USER_ACTIVATION_URL_TEMPLATE': 'http://example.com/#/activate/{user_uuid}/{token}/'
        }

    @staticmethod
    def django_app():
        return 'nodeconductor_plus.nodeconductor_auth'

    @staticmethod
    def django_urls():
        from .urls import urlpatterns
        return urlpatterns
