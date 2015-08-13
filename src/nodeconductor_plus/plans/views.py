import logging
from django.shortcuts import redirect
import django_filters
from django_fsm import TransitionNotAllowed
from rest_framework import viewsets, permissions, mixins, exceptions, status, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from nodeconductor.billing.backend import BillingBackend
from nodeconductor.structure import filters as structure_filters
from nodeconductor_plus.plans.models import Plan, Agreement
from nodeconductor_plus.plans.serializers import PlanSerializer, AgreementSerializer

from . import tasks


logger = logging.getLogger(__name__)


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)

    def filter_queryset(self, queryset):
        return queryset.exclude(backend_id__isnull=True)


class AgreementFilter(django_filters.FilterSet):
    customer = django_filters.CharFilter(
        name='customer__uuid',
        distinct=True,
    )

    class Meta(object):
        model = Agreement
        fields = ['customer']


class AgreementViewSet(mixins.CreateModelMixin,
                       mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    queryset = Agreement.objects.all()
    serializer_class = AgreementSerializer
    lookup_field = 'uuid'
    filter_backends = (structure_filters.GenericRoleFilter, filters.DjangoFilterBackend)
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
    filter_class = AgreementFilter
    backend = BillingBackend()

    def perform_create(self, serializer):
        """
        Create new billing agreement
        """
        customer = serializer.validated_data['customer']
        if not customer.has_user(self.request.user) and not self.request.user.is_staff:
            raise exceptions.PermissionDenied('You do not have permission to perform this action')

        serializer.is_valid(raise_exception=True)
        if not serializer.validated_data['plan'].backend_id:
            raise exceptions.ValidationError('Plan is not synced with backend')

        agreement = serializer.save()
        tasks.push_agreement.delay(agreement.pk)

    def get_pending_agreement(self):
        token = self.request.query_params.get('token')
        if token:
            try:
                return self.get_queryset().get(token=token, state=Agreement.States.PENDING)
            except Agreement.DoesNotExist:
                logger.warning('Unable to find pending agreement with token %s', token)

    @list_route()
    def approve(self, request):
        """
        Callback view for billing agreement approval.
        Do not use it directly. It is internal API.
        """
        agreement = self.get_pending_agreement()
        if agreement:
            try:
                agreement.set_approved()
                agreement.save()
                tasks.activate_agreement.delay(agreement.pk)
            except TransitionNotAllowed:
                logger.warning('Invalid agreement state')

        return redirect(self.backend.return_url)

    @list_route()
    def cancel(self, request):
        """
        Callback view for billing agreement cancel.
        Do not use it directly. It is internal API.
        """
        agreement = self.get_pending_agreement()
        if agreement:
            try:
                agreement.set_cancelled()
            except TransitionNotAllowed:
                logger.warning('Invalid agreement state')

        return redirect(self.backend.return_url)

    @detail_route()
    def transactions(self, request, uuid):
        agreement = self.get_object()
        txs = self.backend.get_agreement_transactions(agreement.backend_id, agreement.created_at)
        return Response(txs, status=status.HTTP_200_OK)
