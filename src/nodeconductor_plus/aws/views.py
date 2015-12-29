from rest_framework import viewsets

from nodeconductor.structure import views as structure_views

from . import filters, models, serializers


class AmazonServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.AWSService.objects.all()
    serializer_class = serializers.ServiceSerializer
    import_serializer_class = serializers.InstanceImportSerializer


class AmazonServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.AWSServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class RegionViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    lookup_field = 'uuid'


class ImageViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    filter_class = filters.ImageFilter
    lookup_field = 'uuid'


class SizeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Size.objects.all()
    serializer_class = serializers.SizeSerializer
    filter_class = filters.SizeFilter
    lookup_field = 'uuid'


class InstanceViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Instance.objects.all()
    serializer_class = serializers.InstanceSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            region=serializer.validated_data['region'],
            image=serializer.validated_data['image'],
            size=serializer.validated_data['size'],
            ssh_key=serializer.validated_data.get('ssh_public_key'))
