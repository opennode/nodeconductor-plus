from nodeconductor.core import NodeConductorExtension


class PlansExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'nodeconductor_plus.plans'

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
