from nodeconductor.core import NodeConductorExtension


class GitLabExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'nodeconductor_plus.gitlab'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in

    @staticmethod
    def celery_tasks():
        from datetime import timedelta
        return {
            'update-gitlab-statistics': {
                'task': 'nodeconductor.gitlab.update_statistics',
                'schedule': timedelta(minutes=60),
                'args': (),
            }
        }
