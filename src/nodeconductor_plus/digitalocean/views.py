from __future__ import unicode_literals

from rest_framework import viewsets, exceptions, permissions, filters

from nodeconductor.core import mixins as core_mixins
from nodeconductor.core.models import SynchronizationStates
from nodeconductor.structure.models import CustomerRole
from nodeconductor.structure.tasks import sync_services
from nodeconductor.structure import filters as structure_filters

from . import models, serializers


class ServiceViewSet(core_mixins.UpdateOnlyStableMixin, viewsets.ModelViewSet):
    queryset = models.DigitalOceanService.objects.all()
    serializer_class = serializers.ServiceSerializer
    lookup_field = 'uuid'
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoObjectPermissions,
    )
    filter_backends = (structure_filters.GenericRoleFilter, filters.DjangoFilterBackend)

    def _can_create_or_update_service(self, serializer):
        customer = serializer.validated_data.get('customer') or serializer.instance.customer
        if self.request.user.is_staff:
            return True
        if customer.has_user(self.request.user, CustomerRole.OWNER):
            return True

    def perform_create(self, serializer):
        if not self._can_create_or_update_service(serializer):
            raise exceptions.PermissionDenied()
        service = serializer.save(state=SynchronizationStates.IN_SYNC)
        sync_services.delay([service.uuid.hex])

    def perform_update(self, serializer):
        if not self._can_create_or_update_service(serializer):
            raise exceptions.PermissionDenied()
        super(ServiceViewSet, self).perform_update(serializer)


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    lookup_field = 'uuid'
