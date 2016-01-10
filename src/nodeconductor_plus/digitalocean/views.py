from __future__ import unicode_literals

from nodeconductor.structure import filters as structure_filters
from nodeconductor.structure import views as structure_views

from . import models, serializers


class DigitalOceanServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.DigitalOceanService.objects.all()
    serializer_class = serializers.ServiceSerializer
    import_serializer_class = serializers.DropletImportSerializer


class DigitalOceanServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.DigitalOceanServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class ImageFilter(structure_filters.BaseServicePropertyFilter):

    class Meta(object):
        model = models.Image
        fields = structure_filters.BaseServicePropertyFilter.Meta.fields + ('distribution', 'type')
        order_by = (
            'distribution',
            'type',
            # desc
            '-distribution',
            '-type',
        )


class ImageViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    filter_class = ImageFilter
    lookup_field = 'uuid'


class RegionViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return models.Region.objects.order_by('name')


class SizeViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Size.objects.all()
    serializer_class = serializers.SizeSerializer
    lookup_field = 'uuid'


class DropletViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Droplet.objects.all()
    serializer_class = serializers.DropletSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            region=serializer.validated_data['region'],
            image=serializer.validated_data['image'],
            size=serializer.validated_data['size'],
            ssh_key=serializer.validated_data.get('ssh_public_key'))
