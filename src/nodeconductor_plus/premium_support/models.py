from django.db import models
from django_fsm import transition, FSMIntegerField
from django.conf import settings
from model_utils.models import TimeStampedModel
from model_utils.fields import AutoCreatedField
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from nodeconductor.core.models import UuidMixin, NameMixin, DescribableMixin
from nodeconductor.structure.models import Project, Resource


def get_resource_models():
    return [m for m in models.get_models() if issubclass(m, Resource)]


class Plan(UuidMixin, NameMixin, DescribableMixin):
    base_rate = models.DecimalField(decimal_places=2, max_digits=10)
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
