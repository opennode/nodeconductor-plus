from __future__ import unicode_literals

from rest_framework import viewsets, permissions, filters, mixins

from nodeconductor.core import mixins as core_mixins
from nodeconductor.structure import filters as structure_filters
from nodeconductor.structure.views import BaseResourceViewSet

from . import models, serializers


class ServiceViewSet(core_mixins.UserContextMixin, viewsets.ModelViewSet):
    queryset = models.DigitalOceanService.objects.all()
    serializer_class = serializers.ServiceSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
    filter_backends = (structure_filters.GenericRoleFilter, filters.DjangoFilterBackend)


class ServiceProjectLinkViewSet(mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                viewsets.GenericViewSet):

    queryset = models.DigitalOceanServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer
    filter_backends = (structure_filters.GenericRoleFilter, filters.DjangoFilterBackend)
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    lookup_field = 'uuid'


class RegionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    lookup_field = 'uuid'


class SizeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Size.objects.all()
    serializer_class = serializers.SizeSerializer
    lookup_field = 'uuid'


class DropletViewSet(BaseResourceViewSet):
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
