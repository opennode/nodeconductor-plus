import logging

import django_filters
from django_fsm import TransitionNotAllowed
from rest_framework import viewsets, permissions, mixins, exceptions, status, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from nodeconductor.structure import filters as structure_filters
from nodeconductor.structure import models as structure_models
from nodeconductor_paypal.backend import PaypalBackend

from .log import event_logger
from .models import Plan, Agreement
from .serializers import PlanSerializer, AgreementSerializer, TokenSerializer
from . import utils

logger = logging.getLogger(__name__)


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Plan.objects.order_by('price')


class AgreementFilter(django_filters.FilterSet):
    customer = django_filters.CharFilter(
        name='customer__uuid',
        distinct=True,
    )

    class Meta(object):
        model = Agreement
        fields = ['customer', 'state']


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

    def get_queryset(self):
        queryset = super(AgreementViewSet, self).get_queryset()
        queryset = queryset.exclude(state=Agreement.States.CANCELLED)

        if not self.request.user.is_staff:
            queryset = queryset.filter(
                customer__roles__permission_group__user=self.request.user,
                customer__roles__role_type=structure_models.CustomerRole.OWNER)
        return queryset

    def perform_create(self, serializer):
        """
        Create new billing agreement
        """
        return_url = serializer.validated_data.pop('return_url')
        cancel_url = serializer.validated_data.pop('cancel_url')
        customer = serializer.validated_data['customer']

        if not customer.has_user(self.request.user) and not self.request.user.is_staff:
            raise exceptions.PermissionDenied('You do not have permission to perform this action')

        agreement = serializer.save()
        utils.create_plan_and_agreement(return_url, cancel_url, agreement)
        serializer.object = agreement

    def get_agreement(self, request):
        """
        Find pending billing plan agreement object in the database by request.
        """
        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']

        try:
            return self.get_queryset().get(token=token, state=Agreement.States.PENDING)
        except Agreement.DoesNotExist:
            raise NotFound("Agreement with token %s does not exist" % token)

    @list_route(methods=['POST'])
    def approve(self, request):
        agreement = self.get_agreement(request)

        try:
            agreement.set_approved()
            agreement.save()
            utils.activate_agreement(agreement)

            event_logger.plan_agreement.info(
                'Billing plan agreement for {customer_name} has been activated.',
                event_type='agreement_approve_succeeded',
                event_context={'agreement': agreement}
            )
            return Response({'status': 'Billing plan agreement has been activated.'})
        except TransitionNotAllowed:
            logger.warning('Unable to approve agreement with ID %s because it has state %s',
                           agreement.pk, agreement.state)
            return Response({'status': 'Invalid agreement state.'},
                            status=status.HTTP_409_CONFLICT)

    @list_route(methods=['POST'])
    def cancel(self, request):
        agreement = self.get_agreement(request)

        try:
            agreement.set_cancelled()
            agreement.save()

            event_logger.plan_agreement.info(
                'Billing plan agreement for {customer_name} has been cancelled.',
                event_type='agreement_cancel_succeeded',
                event_context={'agreement': agreement}
            )

            return Response({'status': 'Billing plan agreement has been cancelled.'})
        except TransitionNotAllowed:
            logger.warning('Unable to cancel agreement with ID %s because it has state %s',
                           agreement.pk, agreement.state)
            return Response({'status': 'Invalid agreement state.'},
                            status=status.HTTP_409_CONFLICT)

    @detail_route()
    def transactions(self, request, uuid):
        agreement = self.get_object()
        txs = PaypalBackend().get_agreement_transactions(agreement.backend_id, agreement.created)
        return Response(txs, status=status.HTTP_200_OK)
