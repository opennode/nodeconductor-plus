from django.conf import settings
from django.db import models, transaction, IntegrityError
from django.utils.encoding import python_2_unicode_compatible
from django_fsm import FSMField, transition

from nodeconductor.core.models import UuidMixin
from nodeconductor.structure import models as structure_models


@python_2_unicode_compatible
class Plan(UuidMixin, models.Model):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return self.name


class PlanQuota(models.Model):
    plan = models.ForeignKey(Plan, related_name='quotas')
    name = models.CharField(max_length=50, choices=[(q, q) for q in structure_models.Customer.QUOTAS_NAMES])
    value = models.FloatField()

    class Meta:
        unique_together = (('plan', 'name'),)


class PlanCustomer(models.Model):
    plan = models.ForeignKey(Plan, related_name='plan_customers')
    customer = models.OneToOneField(structure_models.Customer, related_name='+')


class Order(UuidMixin, models.Model):
    class States(object):
        PROCESSING = 'processing'
        FAILED = 'failed'
        COMPLETED = 'completed'
        ERRED = 'erred'

        CHOICES = (
            (PROCESSING, 'Processing'),
            (FAILED, 'Failed'),
            (COMPLETED, 'Completed'),
            (ERRED, 'Erred'),
        )

    customer = models.ForeignKey(structure_models.Customer, null=True)
    customer_name = models.CharField(max_length=150)
    plan = models.ForeignKey(Plan, related_name='orders', null=True)
    plan_name = models.CharField(max_length=120)
    plan_price = models.DecimalField(max_digits=12, decimal_places=2)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    state = FSMField(
        default=States.PROCESSING, max_length=20, choices=States.CHOICES,
        help_text="WARNING! Should not be changed manually unless you really know what you are doing.")

    @transition(field=state, source=States.PROCESSING, target=States.COMPLETED)
    def _set_completed(self):
        pass

    @transition(field=state, source=States.PROCESSING, target=States.FAILED)
    def _set_failed(self):
        pass

    @transition(field=state, source=States.PROCESSING, target=States.ERRED)
    def _set_erred(self):
        pass

    def execute(self):
        if self.plan is None or self.customer is None:
            self._set_erred()

        with transaction.atomic():
            PlanCustomer.objects.create(plan=self.plan, customer=self.customer)
            self._set_completed()
            self.save()

    def _pre_populate_customer_fields(self):
        if self.customer is None:
            raise IntegrityError('order.customer can not be NULL on order creation')
        self.customer_name = self.customer.name

    def _pre_populate_plan_fields(self):
        if self.plan is None:
            raise IntegrityError('order.plan can not be NULL on order creation')
        self.plan_name = self.plan.name
        self.plan_price = self.plan.price

    def save(self, **kwargs):
        if self.id is None:
            self._pre_populate_customer_fields()
            self._pre_populate_plan_fields()
        return super(Order, self).save(**kwargs)
