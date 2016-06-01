from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django_fsm import transition, FSMIntegerField
from model_utils.models import TimeStampedModel
from model_utils.fields import AutoCreatedField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from nodeconductor.core.models import UuidMixin, NameMixin, DescribableMixin
from nodeconductor.logging.loggers import LoggableMixin
from nodeconductor.structure.models import Project


@python_2_unicode_compatible
class Plan(UuidMixin, NameMixin, DescribableMixin, LoggableMixin):
    base_rate = models.DecimalField(decimal_places=2, max_digits=10)
    hour_rate = models.DecimalField(decimal_places=2, max_digits=10)
    terms = models.TextField()

    def __str__(self):
        return self.name


class Contract(UuidMixin, LoggableMixin):

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

    project = models.ForeignKey(Project)
    plan = models.ForeignKey(Plan)
    state = FSMIntegerField(default=States.REQUESTED, choices=STATE_CHOICES)

    @transition(field=state, source=(States.REQUESTED, States.APPROVED), target=States.CANCELLED)
    def cancel(self):
        pass

    @transition(field=state, source=States.REQUESTED, target=States.APPROVED)
    def approve(self):
        pass

    def get_log_fields(self):
        return ('uuid', 'project', 'plan')


class SupportCase(UuidMixin, NameMixin, DescribableMixin, TimeStampedModel):

    class Permissions(object):
        customer_path = 'contract__project__customer'

    contract = models.ForeignKey(Contract)

    # optional reference to the resource
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    resource = GenericForeignKey('content_type', 'object_id')


class Worklog(UuidMixin, DescribableMixin):

    class Permissions(object):
        customer_path = 'support_case__contract__project__customer'

    created = AutoCreatedField()
    time_spent = models.PositiveIntegerField()
    support_case = models.ForeignKey(SupportCase)
