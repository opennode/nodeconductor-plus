from django.conf import settings
from django_fsm import TransitionNotAllowed
from rest_framework import viewsets, permissions, mixins, exceptions, response, status
from rest_framework.decorators import detail_route

from nodeconductor.structure import models as structure_models
import models
import serializers


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Plan.objects.all()
    serializer_class = serializers.PlanSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)


class OrderViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    queryset = models.Order.objects.all()
    serializer_class = serializers.OrderSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = super(OrderViewSet, self).get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                customer__roles__permission_group__user=self.request.user,
                customer__roles__role_type=structure_models.CustomerRole.OWNER)
        return queryset

    def perform_create(self, serializer):
        customer = serializer.validated_data['customer']
        if not customer.has_user(self.request.user) and not self.request.user.is_staff:
            raise exceptions.PermissionDenied('You do not have permission to perform this action.')

        super(OrderViewSet, self).perform_create(serializer)

    @detail_route(methods=['post'])
    def execute(self, request, uuid):
        try:
            is_dummy_payments_enabled = settings.NODECONDUCTOR.get('PAYMENTS_DUMMY', False)
        except KeyError:
            is_dummy_payments_enabled = False

        if not is_dummy_payments_enabled:
            raise exceptions.NotFound()

        order = self.get_object()
        try:
            order.execute()
        except TransitionNotAllowed:
            return response.Response(
                {'detail': 'Only processing order can be executed'}, status=status.HTTP_409_CONFLICT)
        return response.Response({'detail': 'Order was successfully executed'}, status=status.HTTP_200_OK)
