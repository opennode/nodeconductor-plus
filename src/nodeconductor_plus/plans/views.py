import datetime
import logging
from django.conf import settings
from django.shortcuts import redirect
import django_filters
from django_fsm import TransitionNotAllowed
from rest_framework import viewsets, permissions, mixins, exceptions, response, status, filters
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework.reverse import reverse

from nodeconductor.billing.backend import BillingBackend, BillingBackendError
from nodeconductor.structure import filters as structure_filters,  models as structure_models
from . import models, serializers


logger = logging.getLogger(__name__)


class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Plan.objects.all()
    serializer_class = serializers.PlanSerializer
    lookup_field = 'uuid'
    permission_classes = (permissions.IsAuthenticated,)


class PlanCustomerFilter(django_filters.FilterSet):
    customer = django_filters.CharFilter(
        name='customer__uuid',
        distinct=True,
    )

    class Meta(object):
        model = models.PlanCustomer
        fields = ['customer']


class PlanCustomerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.PlanCustomer.objects.all()
    serializer_class = serializers.PlanCustomerSerializer
    lookup_field = 'uuid'
    filter_backends = (structure_filters.GenericRoleFilter, filters.DjangoFilterBackend)
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoObjectPermissions)
    filter_class = PlanCustomerFilter


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
        """
        Create new order for billing agreement
        """
        customer = serializer.validated_data['customer']
        if not customer.has_user(self.request.user) and not self.request.user.is_staff:
            raise exceptions.PermissionDenied('You do not have permission to perform this action.')

        order = serializer.save()
        plan = order.plan
        backend = BillingBackend()

        if not plan.backend_id:
            base_url = reverse('order-list', request=self.request)
            return_url = base_url + 'approve/'
            cancel_url = base_url + 'cancel/'

            backend_id = backend.create_plan(amount=plan.price,
                                             name=plan.name,
                                             description=plan.name,
                                             return_url=return_url,
                                             cancel_url=cancel_url)
            plan.backend_id = backend_id
            plan.save()

        approval_url, token = backend.create_agreement(plan.backend_id, plan.name)
        order.approval_url = approval_url
        order.token = token
        order.set_pending()
        order.save()

    @list_route()
    def approve(self, request):
        """
        Callback view for billing agreement approval.
        Do not use it directly. It is internal API.
        """

        backend = BillingBackend()
        token = self.request.query_params.get('token')
        if not token:
            logger.warning('Unable to approve order because token is missing')
            return redirect(backend.return_url)

        try:
            order = self.get_queryset().get(token=token,
                                            backend_id__isnull=True,
                                            state=models.Order.States.PENDING)
        except models.Order.DoesNotExist:
            logger.warning('Unable to find order by token')
            return redirect(backend.return_url)


        # Customer should have only one active order at time
        # That's why we need to cancel old order before activating new one
        try:
            old_order = models.Order.objects.get(customer=order.customer,
                                                 backend_id__isnull=False,
                                                 state=models.Order.States.ACTIVE)
            backend.cancel_agreement(old_order.backend_id)
            old_order.set_cancelled()
            old_order.save()
        except BillingBackendError:
            logger.warning('Unable to cancel old order because of backend error')
            old_order.set_erred()
            old_order.save()
            return redirect(backend.return_url)
        except models.Order.DoesNotExist:
            # It's ok if we don't have any active order for customer
            logger.info('There is no active order for customer')
        else:
            logger.info('Old order has been cancelled')

        try:
            order.backend_id = backend.execute_agreement(token)
            order.execute()
        except BillingBackendError:
            logger.warning('Unable to execute order because of backend error')
            order.set_erred()
            order.save()
        else:
            logger.info('New order has been activated')
        return redirect(backend.return_url)

    @list_route()
    def cancel(self, request):
        """
        Callback view for billing agreement cancel.
        Do not use it directly. It is internal API.
        """

        backend = BillingBackend()
        token = self.request.query_params.get('token')
        if not token:
            logger.warning('Unable to approve order because token is missing')
            return redirect(backend.return_url)

        try:
            order = self.get_queryset().get(token=token,
                                            backend_id__isnull=True,
                                            state=models.Order.States.PENDING)
        except models.Order.DoesNotExist:
            logger.warning('Unable to find order by token')
            return redirect(backend.return_url)

        try:
            order.set_cancelled()
            order.save()
        except TransitionNotAllowed:
            logger.warning('Only pending order can be executed')
        return redirect(BillingBackend().return_url)

    @detail_route()
    def transactions(self, request, uuid):
        order = self.get_object()
        backend = BillingBackend()
        txs = backend.get_agreement_transactions(order.backend_id,
                                                 order.start_date,
                                                 datetime.datetime.now())
        return Response(txs, status=status.HTTP_200_OK)
