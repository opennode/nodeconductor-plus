import datetime
import collections

from django_fsm import TransitionNotAllowed
from rest_framework import mixins, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.exceptions import PermissionDenied

from nodeconductor.structure import models as structure_models
from nodeconductor.structure.filters import GenericRoleFilter
from nodeconductor_plus.premium_support import models, serializers


class PlanViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  viewsets.GenericViewSet):
    queryset = models.Plan.objects.all()
    serializer_class = serializers.PlanSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)


class SupportContractViewSet(mixins.CreateModelMixin,
                             mixins.RetrieveModelMixin,
                             mixins.ListModelMixin,
                             viewsets.GenericViewSet):
    queryset = models.Contract.objects.all()
    serializer_class = serializers.ContractSerializer
    filter_backends = (GenericRoleFilter,)
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)

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

    @detail_route(methods=['get'])
    def report(self, request, uuid):
        contract = self.get_object()
        hours_per_month = collections.defaultdict(int)
        items = models.Worklog.objects.filter(support_case__contract=contract).values('time_spent', 'created')
        for item in items:
            month = datetime.date(item['created'].year, item['created'].month, 1)
            hours_per_month[month] += item['time_spent']

        rows = []
        for month, hours in hours_per_month.items():
            rows.append({'date': month, 'hours': hours, 'price': hours * contract.plan.hour_rate})

        serializer = serializers.ReportSerializer(rows, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SupportCaseViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.ListModelMixin,
                         viewsets.GenericViewSet):
    queryset = models.SupportCase.objects.all()
    serializer_class = serializers.SupportCaseSerializer
    filter_backends = (GenericRoleFilter,)
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        user = self.request.user
        contract = serializer.validated_data['contract']

        if not contract.project.customer.has_user(user) and not user.is_staff:
            raise PermissionDenied('Access to the project is denied for current user')

        serializer.save()


class SupportWorklogViewSet(mixins.CreateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    queryset = models.Worklog.objects.all()
    serializer_class = serializers.WorklogSerializer
    filter_backends = (GenericRoleFilter,)
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)

    def perform_create(self, serializer):
        user = self.request.user
        support_case = serializer.validated_data['support_case']

        if not support_case.contract.project.customer.has_user(user) and not user.is_staff:
            raise PermissionDenied('Access to the project is denied for current user')

        serializer.save()
