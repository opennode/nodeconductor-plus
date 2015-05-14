from __future__ import unicode_literals

from rest_framework import viewsets, exceptions, permissions

from nodeconductor.core import mixins as core_mixins
from nodeconductor.core.tasks import send_task
from nodeconductor.core.models import SynchronizationStates
from nodeconductor.structure import models as structure_models

from . import models, serializers


class ServiceViewSet(core_mixins.UpdateOnlyStableMixin, viewsets.ModelViewSet):
    queryset = models.DigitalOceanService.objects.all()
    serializer_class = serializers.ServiceSerializer
    lookup_field = 'uuid'
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.DjangoObjectPermissions,
    )

    def _can_create_or_update_service(self, serializer):
        if self.request.user.is_staff:
            return True
        if serializer.validated_data['customer'].has_user(
                self.request.user, structure_models.CustomerRole.OWNER):
            return True

    def perform_create(self, serializer):
        if not self._can_create_or_update_service(serializer):
            raise exceptions.PermissionDenied()
        cloud = serializer.save(state=SynchronizationStates.IN_SYNC)
        send_task('structure', 'sync_services')([cloud.uuid.hex])

    def perform_update(self, serializer):
        if not self._can_create_or_update_service(serializer):
            raise exceptions.PermissionDenied()
        super(ServiceViewSet, self).perform_update(serializer)
