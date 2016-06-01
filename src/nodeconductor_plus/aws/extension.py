from nodeconductor.core import NodeConductorExtension


class AWSExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'nodeconductor_plus.aws'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in
