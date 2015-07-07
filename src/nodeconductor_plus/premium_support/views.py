from django_fsm import TransitionNotAllowed
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import PermissionDenied

from nodeconductor.structure import models as structure_models
from nodeconductor_plus.premium_support import models, serializers


class PlanViewSet(viewsets.ModelViewSet):
    queryset = models.Plan.objects.all()
    serializer_class = serializers.PlanSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)


class SupportContractViewSet(mixins.CreateModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    queryset = models.Contract.objects.all()
    serializer_class = serializers.ContractSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = super(SupportContractViewSet, self).get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                project__customer__roles__permission_group__user=self.request.user,
                project__customer__roles__role_type=structure_models.CustomerRole.OWNER)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        project = serializer.validated_data['project']
        if not project.customer.has_user(user) and not user.is_staff:
            raise PermissionDenied('Access to the project is denied for current user')
        serializer.save()

    @detail_route(methods=['post'])
    def cancel(self, request, uuid):
        contract = self.get_object()
        try:
            contract.cancel()
        except TransitionNotAllowed:
            return Response({'detail': 'Unable to cancel support contract'}, status=status.HTTP_409_CONFLICT)
        return Response({'detail': 'Support contract has been cancelled'}, status=status.HTTP_200_OK)

    @detail_route(methods=['post'])
    def approve(self, request, uuid):
        if not request.user.is_staff:
            raise PermissionDenied('Only staff can approve support contract')
        contract = self.get_object()
        try:
            contract.approve()
        except TransitionNotAllowed:
            return Response({'detail': 'Unable to approve support contract'}, status=status.HTTP_409_CONFLICT)
        return Response({'detail': 'Support contract has been approved'}, status=status.HTTP_200_OK)
