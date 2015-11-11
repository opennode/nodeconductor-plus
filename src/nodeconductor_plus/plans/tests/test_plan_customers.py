from rest_framework import test, status

from . import factories
from .. import models
from nodeconductor.structure import models as structure_models
from nodeconductor.structure.tests import factories as structure_factories


class PlanCustomerListTest(test.APITransactionTestCase):

    def setUp(self):
        self.user = structure_factories.UserFactory()

        self.customer = structure_factories.CustomerFactory()
        self.owner = structure_factories.UserFactory()
        self.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)

        self.project_group = structure_factories.ProjectGroupFactory(customer=self.customer)
        self.group_manager = structure_factories.UserFactory()
        self.project_group.add_user(self.group_manager, structure_models.ProjectGroupRole.MANAGER)

        self.project = structure_factories.ProjectFactory(customer=self.customer)
        self.admin = structure_factories.UserFactory()
        self.project.add_user(self.admin, structure_models.ProjectRole.ADMINISTRATOR)

        self.plan = factories.PlanFactory()

    def test_customer_owner_can_see_his_customer_plan(self):
        plan_customer = models.PlanCustomer.objects.get(customer=self.customer)

        self.client.force_authenticate(self.owner)
        response = self.client.get(factories.PlanCustomerFactory.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(plan_customer.uuid.hex, [el['uuid'] for el in response.data])

    def test_project_admin_can_see_his_project_customer_plan(self):
        plan_customer = models.PlanCustomer.objects.get(customer=self.customer)

        self.client.force_authenticate(self.admin)
        response = self.client.get(factories.PlanCustomerFactory.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(plan_customer.uuid.hex, [el['uuid'] for el in response.data])

    def test_project_group_manager_can_see_his_project_group_customer_plan(self):
        plan_customer = models.PlanCustomer.objects.get(customer=self.customer)

        self.client.force_authenticate(self.group_manager)
        response = self.client.get(factories.PlanCustomerFactory.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(plan_customer.uuid.hex, [el['uuid'] for el in response.data])

    def test_customer_owner_can_not_see_plan_of_other_customers(self):
        other_customer = structure_factories.CustomerFactory()
        plan_customer = models.PlanCustomer.objects.get(customer=other_customer)

        self.client.force_authenticate(self.owner)
        response = self.client.get(factories.PlanCustomerFactory.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(plan_customer.uuid.hex, [el['uuid'] for el in response.data])
