from django.db import models

from nodeconductor.core.models import UuidMixin
from nodeconductor.structure import models as structure_models


class Plan(UuidMixin, models.Model):
    name = models.CharField(max_length=120)
    price = models.DecimalField(max_digits=12, decimal_places=2)


class PlanQuota(models.Model):
    plan = models.ForeignKey(Plan, related_name='quotas')
    name = models.CharField(max_length=50, choices=[(q, q) for q in structure_models.Customer.QUOTAS_NAMES])
    value = models.FloatField()


class PlanCustomer(models.Model):
    plan = models.ForeignKey(Plan, related_name='plan_customers')
    customer = models.OneToOneField(structure_models.Customer, related_name='+')
