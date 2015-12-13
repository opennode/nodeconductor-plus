from django.test import TestCase

from .. import factories
from ... import models
from nodeconductor.structure.tests.factories import CustomerFactory


class HandlersTest(TestCase):

    def test_default_plan_is_added_to_customer_on_creation(self):
        default_plan = factories.PlanFactory(is_default=True)
        customer = CustomerFactory()

        self.assertTrue(models.Agreement.objects.filter(
            plan=default_plan, customer=customer, state=models.Agreement.States.ACTIVE).exists())
