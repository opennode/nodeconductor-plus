from django_fsm import TransitionNotAllowed
from rest_framework import viewsets, permissions, exceptions, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route

from nodeconductor_plus.premium_support import models, serializers


class PlanViewSet(viewsets.ModelViewSet):
    queryset = models.Plan.objects.all()
    serializer_class = serializers.PlanSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)


class ContractViewSet(viewsets.ModelViewSet):
    queryset = models.Contract.objects.all()
    serializer_class = serializers.ContractSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)

    @detail_route(methods=['post'])
    def cancel(self, request, uuid):
        contract = self.get_object()
        try:
            contract.cancel()
        except TransitionNotAllowed:
            return Response({'detail': 'Unable to cancel contract'}, status=status.HTTP_409_CONFLICT)
        return Response({'detail': 'Contract has been cancelled'}, status=status.HTTP_200_OK)
