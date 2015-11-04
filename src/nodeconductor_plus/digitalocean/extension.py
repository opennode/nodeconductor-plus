from nodeconductor.core import NodeConductorExtension


class DigitalOceanExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'nodeconductor_plus.digitalocean'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in
