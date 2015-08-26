from __future__ import unicode_literals

import django_filters

from rest_framework import viewsets

from nodeconductor.structure import views as structure_views

from . import models, serializers


class DigitalOceanServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.DigitalOceanService.objects.all()
    serializer_class = serializers.ServiceSerializer
    import_serializer_class = serializers.DropletImportSerializer


class DigitalOceanServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.DigitalOceanServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class ImageFilter(django_filters.FilterSet):

    class Meta(object):
        model = models.Image
        fields = 'distribution', 'type'
        order_by = (
            'distribution',
            'type',
            # desc
            '-distribution',
            '-type',
        )


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    filter_class = ImageFilter
    lookup_field = 'uuid'


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    lookup_field = 'uuid'


class SizeViewSet(viewsets.ReadOnlyModelViewSet):
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
