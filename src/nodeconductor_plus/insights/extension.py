from nodeconductor.core import NodeConductorExtension


class InsightsExtension(NodeConductorExtension):

    class Settings:
        NODECONDUCTOR_INSIGHTS = {
            'PROJECTED_COSTS_EXCESS': 20,
        }

    @staticmethod
    def django_app():
        return 'nodeconductor_plus.insights'

    @staticmethod
    def celery_tasks():
        from datetime import timedelta
        return {
            'check-services': {
                'task': 'nodeconductor.insights.check_services',
                'schedule': timedelta(minutes=60),
                'args': ()
            },
            'check-customers': {
                'task': 'nodeconductor.insights.check_customers',
                'schedule': timedelta(hours=24),
                'args': (),
            },
        }
