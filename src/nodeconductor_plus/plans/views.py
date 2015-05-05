from rest_framework import viewsets, permissions

from . import models, serializers
from nodeconductor.structure import filters as structure_filters


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Plan.objects.all()
    serializer_class = serializers.PlanSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)


class PlanCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.PlanCustomer.objects.all()
    serializer_class = serializers.PlanCustomerSerializer
    lookup_field = 'uuid'
    filter_backends = (structure_filters.GenericRoleFilter,)
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
