from nodeconductor.core import NodeConductorExtension


class PlansExtension(NodeConductorExtension):

    class Settings:
        NODECONDUCTOR_PLANS = {
            'APPROVAL_URL_TEMPLATE': 'http://example.com/#/approve-billing-plan/{token}/',
            'CANCEL_URL_TEMPLATE': 'http://example.com/#/cancel-billing-plan/{token}/'
        }

    @staticmethod
    def django_app():
        return 'nodeconductor_plus.plans'

    @staticmethod
    def django_urls():
        from .urls import urlpatterns
        return urlpatterns

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in

    @staticmethod
    def celery_tasks():
        from datetime import timedelta
        return {
            'check-agreements': {
                'task': 'nodeconductor.plans.check_agreements',
                'schedule': timedelta(minutes=60),
                'args': (),
            }
        }
