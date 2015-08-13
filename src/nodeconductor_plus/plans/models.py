import logging

from django.conf import settings
from django.db import models, transaction, IntegrityError
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django_fsm import FSMField, transition
from model_utils.models import TimeStampedModel
from rest_framework.reverse import reverse

from nodeconductor.billing.backend import BillingBackend
from nodeconductor.core.models import UuidMixin
from nodeconductor.structure import models as structure_models
from nodeconductor_plus.plans.settings import DEFAULT_PLAN


logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Plan(UuidMixin, models.Model):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    backend_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.name

    def push_to_backend(self, request):
        base_url = reverse('agreement-list', request=request)
        return_url = base_url + 'approve/'
        cancel_url = base_url + 'cancel/'

        backend = BillingBackend()
        backend_id = backend.create_plan(amount=self.price,
                                         name=self.name,
                                         description=self.name,
                                         return_url=return_url,
                                         cancel_url=cancel_url)
        self.backend_id = backend_id
        self.save()

    @staticmethod
    def get_or_create_default_plan():
        default_plan, created = Plan.objects.get_or_create(
            name=DEFAULT_PLAN['name'], price=DEFAULT_PLAN['price'])
        if created:
            for quota_name, quota_value in DEFAULT_PLAN['quotas']:
                PlanQuota.objects.get_or_create(name=quota_name, value=quota_value, plan=default_plan)
        return default_plan


class PlanQuota(models.Model):
    plan = models.ForeignKey(Plan, related_name='quotas')
    name = models.CharField(max_length=50, choices=[(q, q) for q in structure_models.Customer.QUOTAS_NAMES])
    value = models.FloatField()

    class Meta:
        unique_together = (('plan', 'name'),)


class Agreement(UuidMixin, TimeStampedModel):
    class Permissions(object):
        customer_path = 'customer'
        project_path = 'customer__projects'
        project_group_path = 'customer__project_groups'

    class States(object):
        CREATED = 'created' # agreement has been created in our database, but not yet pushed to backend
        PENDING = 'pending' # agreement has been pushed to backend, but not yet approved by user
        APPROVED = 'approved' # agreement has been approved by user but quotas have not been applied
        ACTIVE = 'active' # appropriate quotas have been applied, other agreements (if any) are cancelled
        CANCELLED = 'cancelled'
        ERRED = 'erred'

        CHOICES = (
            (CREATED, 'Created'),
            (PENDING, 'Pending'),
            (APPROVED, 'Approved'),
            (ACTIVE, 'Active'),
            (CANCELLED, 'Cancelled'),
            (ERRED, 'Erred'),
        )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)
    plan = models.ForeignKey(Plan)
    customer = models.ForeignKey(structure_models.Customer)

    # These values are fetched from backend
    backend_id = models.CharField(max_length=255, null=True)

    # Token is used as temporary identifier of billing agreement
    token = models.CharField(max_length=120, null=True)
    approval_url = models.URLField(null=True)

    state = FSMField(default=States.CREATED,
                     max_length=20,
                     choices=States.CHOICES,
                     help_text="WARNING! Should not be changed manually unless you really know what you are doing.")

    @transition(field=state, source=States.CREATED, target=States.PENDING)
    def set_pending(self, approval_url, token):
        self.approval_url = approval_url
        self.token = token

    @transition(field=state, source=States.PENDING, target=States.APPROVED)
    def set_approved(self):
        pass

    @transition(field=state, source=States.APPROVED, target=States.ACTIVE)
    def set_active(self):
        pass

    @transition(field=state, source=(States.PENDING, States.ACTIVE), target=States.CANCELLED)
    def set_cancelled(self):
        pass

    @transition(field=state, source='*', target=States.ERRED)
    def set_erred(self):
        pass

    def apply_quotas(self):
        for quota in self.plan.quotas.all():
            self.customer.set_quota_limit(quota.name, quota.value)

    @staticmethod
    def apply_default_plan(customer):
        default_plan = Plan.get_or_create_default_plan()
        agreement = Agreement.objects.create(
            plan=default_plan, customer=customer, state=Agreement.States.ACTIVE)
        agreement.apply_quotas()
        logger.info('Default plan for customer %s has been applied', self.customer.name)
