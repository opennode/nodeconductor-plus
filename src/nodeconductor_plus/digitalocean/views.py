from __future__ import unicode_literals

import django_filters

from rest_framework import viewsets, permissions, decorators, response, status, filters, mixins

from nodeconductor.core import mixins as core_mixins
from nodeconductor.structure import filters as structure_filters
from nodeconductor.structure.views import BaseResourceViewSet

from . import models, serializers


class DigitalOceanServiceViewSet(core_mixins.UserContextMixin, viewsets.ModelViewSet):
    queryset = models.DigitalOceanService.objects.all()
    serializer_class = serializers.ServiceSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
    filter_backends = (structure_filters.GenericRoleFilter, filters.DjangoFilterBackend)

    def get_serializer_class(self):
        if self.action == 'link':
            return serializers.DropletImportSerializer
        return super(DigitalOceanServiceViewSet, self).get_serializer_class()

    def check_object_permissions(self, request, obj):
        if self.action == 'link' and self.request.method == 'POST':
            return

    @decorators.detail_route(methods=['get', 'post'])
    def link(self, request, uuid=None):
        if self.request.method == 'GET':
            backend = self.get_object().get_backend()
            return response.Response(backend.get_droplets_for_import())
        else:
            serializer = self.get_serializer_class()(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return response.Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DigitalOceanServiceProjectLinkViewSet(mixins.CreateModelMixin,
                                            mixins.RetrieveModelMixin,
                                            mixins.DestroyModelMixin,
                                            mixins.ListModelMixin,
                                            viewsets.GenericViewSet):

    queryset = models.DigitalOceanServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer
    filter_backends = (structure_filters.GenericRoleFilter, filters.DjangoFilterBackend)
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)


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
