from rest_framework import viewsets

from nodeconductor.structure import views as structure_views
from nodeconductor_plus.aws.backend import SizeQueryset

from . import models, serializers


class AmazonServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.AWSService.objects.all()
    serializer_class = serializers.ServiceSerializer
    import_serializer_class = serializers.InstanceImportSerializer


class AmazonServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.AWSServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class ImageViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    lookup_field = 'uuid'


class SizeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SizeQueryset()
    serializer_class = serializers.SizeSerializer
    lookup_field = 'uuid'


class InstanceViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Instance.objects.all()
    serializer_class = serializers.InstanceSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            image=serializer.validated_data['image'],
            size=serializer.validated_data['size'],
            ssh_key=serializer.validated_data.get('ssh_public_key'))
