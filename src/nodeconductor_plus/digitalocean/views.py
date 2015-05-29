from __future__ import unicode_literals

from rest_framework import (
    viewsets, decorators, permissions,
    filters, mixins, response, status)

from nodeconductor.core import mixins as core_mixins
from nodeconductor.core import models as core_models
from nodeconductor.core import exceptions as core_exceptions
from nodeconductor.iaas.models import VirtualMachineStates
from nodeconductor.structure import filters as structure_filters

from . import models, serializers


class ServiceViewSet(core_mixins.UserContextMixin, viewsets.ModelViewSet):
    queryset = models.DigitalOceanService.objects.all()
    serializer_class = serializers.ServiceSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
    filter_backends = (structure_filters.GenericRoleFilter, filters.DjangoFilterBackend)


class ResourceViewSet(core_mixins.UserContextMixin, viewsets.ModelViewSet):
    queryset = models.Droplet.objects.all()
    serializer_class = serializers.ResourceSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
    filter_backends = (structure_filters.GenericRoleFilter, filters.DjangoFilterBackend)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.ResourceCreateSerializer
        return super(ResourceViewSet, self).get_serializer_class()

    def initial(self, request, *args, **kwargs):
        if self.action in ('update', 'partial_update', 'destroy'):
            resource = self.get_object()
            if resource.state not in VirtualMachineStates.STABLE_STATES:
                raise core_exceptions.IncorrectStateException(
                    'Modification allowed in stable states only')

        elif self.action in ('stop', 'start', 'resize'):
            resource = self.get_object()
            if resource.state == VirtualMachineStates.PROVISIONING_SCHEDULED:
                raise core_exceptions.IncorrectStateException(
                    'Provisioning scheduled. Disabled modifications.')

        super(ResourceViewSet, self).initial(request, *args, **kwargs)

    def perform_create(self, serializer):
        if serializer.validated_data['service_project_link'].state == core_models.SynchronizationStates.ERRED:
            raise core_exceptions.IncorrectStateException(
                detail='Cannot modify resource if its service project link in erred state.')

        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            region=serializer.validated_data['region'],
            image=serializer.validated_data['image'],
            size=serializer.validated_data['size'],
            ssh_key=serializer.validated_data.get('ssh_public_key'))

    def perform_update(self, serializer):
        spl = self.get_object().service_project_link
        if spl.state == core_models.SynchronizationStates.ERRED:
            raise core_exceptions.IncorrectStateException(
                detail='Cannot modify resource if its service project link in erred state.')

        serializer.save()

    @decorators.detail_route(methods=['post'])
    def start(self, request, uuid=None):
        resource = models.Droplet.objects.get(uuid=uuid)
        backend = resource.get_backend()
        backend.start()
        return response.Response({'status': 'start was scheduled'}, status=status.HTTP_202_ACCEPTED)

    @decorators.detail_route(methods=['post'])
    def stop(self, request, uuid=None):
        resource = models.Droplet.objects.get(uuid=uuid)
        backend = resource.get_backend()
        backend.stop()
        return response.Response({'status': 'stop was scheduled'}, status=status.HTTP_202_ACCEPTED)

    @decorators.detail_route(methods=['post'])
    def restart(self, request, uuid=None):
        resource = models.Droplet.objects.get(uuid=uuid)
        backend = resource.get_backend()
        backend.restart()
        return response.Response({'status': 'restart was scheduled'}, status=status.HTTP_202_ACCEPTED)


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
