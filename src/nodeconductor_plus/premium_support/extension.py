from nodeconductor.core import NodeConductorExtension


class SupportExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'nodeconductor_plus.premium_support'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in
