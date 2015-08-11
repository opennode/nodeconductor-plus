from django.conf import settings
from django.db import models, transaction, IntegrityError
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django_fsm import FSMField, transition
from model_utils.models import TimeStampedModel

from nodeconductor.core.models import UuidMixin
from nodeconductor.structure import models as structure_models


@python_2_unicode_compatible
class Plan(UuidMixin, models.Model):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    backend_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class PlanQuota(models.Model):
    plan = models.ForeignKey(Plan, related_name='quotas')
    name = models.CharField(max_length=50, choices=[(q, q) for q in structure_models.Customer.QUOTAS_NAMES])
    value = models.FloatField()

    class Meta:
        unique_together = (('plan', 'name'),)


class PlanCustomer(UuidMixin, models.Model):
    class Permissions(object):
        customer_path = 'customer'
        project_path = 'customer__projects'
        project_group_path = 'customer__project_groups'

    plan = models.ForeignKey(Plan, related_name='plan_customers')
    customer = models.OneToOneField(structure_models.Customer, related_name='+')


class Order(UuidMixin, TimeStampedModel):
    class States(object):
        CREATED = 'created' # Order has been created in our database, but not yet pushed to backend
        PENDING = 'pending' # Order has been pushed to backend, but not yet approved by user
        ACTIVE = 'active' # Order has been approved by user and appropriate quotas have been applied
        CANCELLED = 'cancelled'
        ERRED = 'erred'

        CHOICES = (
            (CREATED, 'Created'),
            (PENDING, 'Pending'),
            (ACTIVE, 'Active'),
            (CANCELLED, 'Cancelled'),
            (ERRED, 'Erred'),
        )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    plan = models.ForeignKey(Plan, related_name='orders', null=True, on_delete=models.SET_NULL)
    customer = models.ForeignKey(structure_models.Customer, null=True, on_delete=models.SET_NULL)

    # These fields are used when related objects have been deleted but order is still present
    username = models.CharField(max_length=30)
    plan_name = models.CharField(max_length=120)
    plan_price = models.DecimalField(max_digits=12, decimal_places=2)
    customer_name = models.CharField(max_length=150)

    # These values are fetched from backend
    backend_id = models.CharField(max_length=255, null=True)

    # Token is used as temporary identifier of billing agreement
    token = models.CharField(max_length=120, null=True)
    approval_url = models.URLField(null=True)

    start_date = models.DateTimeField(null=True, help_text='Date when order has been activated')
    end_date = models.DateTimeField(null=True, help_text='Date when order has been cancelled')
    last_transaction_at = models.DateTimeField(null=True)

    state = FSMField(
        default=States.CREATED, max_length=20, choices=States.CHOICES,
        help_text="WARNING! Should not be changed manually unless you really know what you are doing.")

    @transition(field=state, source=States.CREATED, target=States.PENDING)
    def set_pending(self):
        pass

    @transition(field=state, source=States.PENDING, target=States.ACTIVE)
    def set_active(self):
        self.start_date = timezone.now()
        self.last_transaction_at = timezone.now()

    @transition(field=state, source=(States.PENDING, States.ACTIVE), target=States.CANCELLED)
    def set_cancelled(self):
        self.end_date = timezone.now()

    @transition(field=state, source='*', target=States.ERRED)
    def set_erred(self):
        pass

    def execute(self):
        with transaction.atomic():
            self._apply_quotas()
            PlanCustomer.objects.update_or_create(customer=self.customer, defaults={'plan': self.plan})
            self.set_active()
            self.save()

    def _apply_quotas(self):
        for quota in self.plan.quotas.all():
            self.customer.set_quota_limit(quota.name, quota.value)

    def _pre_populate_customer_fields(self):
        if self.customer is None:
            raise IntegrityError('order.customer can not be NULL on order creation')
        self.customer_name = self.customer.name

    def _pre_populate_plan_fields(self):
        if self.plan is None:
            raise IntegrityError('order.plan can not be NULL on order creation')
        self.plan_name = self.plan.name
        self.plan_price = self.plan.price

    def _pre_populate_user_fields(self):
        if self.user is None:
            raise IntegrityError('order.user can not be NULL on order creation')
        self.username = self.user.username

    def save(self, **kwargs):
        if self.id is None:
            self._pre_populate_customer_fields()
            self._pre_populate_plan_fields()
            self._pre_populate_user_fields()
        return super(Order, self).save(**kwargs)
