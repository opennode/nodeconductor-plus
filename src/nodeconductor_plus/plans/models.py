from django.db import models
from django.utils.encoding import python_2_unicode_compatible

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
