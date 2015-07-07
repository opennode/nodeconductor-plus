from django.db import models
from django_fsm import TransitionNotAllowed, FSMIntegerField
from django.conf import settings

from nodeconductor.core.models import UuidMixin
from nodeconductor.structure.models import Project


class Plan(UuidMixin, models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField()
    base_hours = models.IntegerField()
    hour_rate = models.DecimalField(decimal_places=2, max_digits=10)


class Contract(UuidMixin, models.Model):
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

    def cancel(self):
        if self.state in (self.States.REQUESTED, self.States.APPROVED):
            self.state = self.States.CANCELLED
            self.save()
        else:
            raise TransitionNotAllowed()
