from django.db import models
from django_fsm import transition, FSMIntegerField
from django.conf import settings
from model_utils.models import TimeStampedModel

from nodeconductor.core.models import UuidMixin, NameMixin, DescribableMixin
from nodeconductor.structure.models import Project


class Plan(UuidMixin):
    name = models.CharField(max_length=120)
    description = models.TextField()
    base_hours = models.PositiveIntegerField()
    hour_rate = models.DecimalField(decimal_places=2, max_digits=10)


class Contract(UuidMixin):

    class Permissions(object):
        customer_path = 'project__customer'

    class States(object):
        REQUESTED = 1
        APPROVED = 2
        CANCELLED = 3

    STATE_CHOICES = (
        (States.REQUESTED, 'Requested'),
        (States.APPROVED, 'Approved'),
        (States.CANCELLED, 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    project = models.ForeignKey(Project)
    plan = models.ForeignKey(Plan)
    state = FSMIntegerField(default=States.REQUESTED, choices=STATE_CHOICES)

    @transition(field=state, source=(States.REQUESTED, States.APPROVED), target=States.CANCELLED)
    def cancel(self):
        pass

    @transition(field=state, source=States.REQUESTED, target=States.APPROVED)
    def approve(self):
        pass


class SupportCase(UuidMixin, NameMixin, DescribableMixin, TimeStampedModel):

    class Permissions(object):
        customer_path = 'contract__project__customer'

    contract = models.ForeignKey(Contract)
