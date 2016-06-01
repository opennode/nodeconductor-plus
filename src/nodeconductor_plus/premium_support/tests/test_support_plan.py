from rest_framework import status, test

from nodeconductor.structure.tests import factories as structure_factories
from nodeconductor_plus.premium_support.tests import factories as support_factories


class SupportPlanTest(test.APITransactionTestCase):
    def setUp(self):
        self.staff = structure_factories.UserFactory(is_staff=True)
        self.user = structure_factories.UserFactory()
        self.plans = [
            {
                'name': 'Bronze support',
                'terms': 'Gives you access to online documentation, community forums, and billing support.',
                'base_rate': 100,
                'hour_rate': 10
            },
            {
                'name': 'Silver support',
                'terms': 'Gives you direct access to our support team.',
                'base_rate': 200,
                'hour_rate': 20
            },
            {
                'name': 'Gold support',
                'terms': '24x7 phone support, rapid response times and consultation on application development.',
                'base_rate': 300,
                'hour_rate': 30
            }
        ]

    def test_staff_can_create_plan(self):
        self.client.force_authenticate(self.staff)
        for plan in self.plans:
            self.create_plan(plan)

    def test_user_can_not_create_plan(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(support_factories.PlanFactory.get_list_url(), data=self.plans[0])
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_not_delete_plan(self):
        self.client.force_authenticate(self.staff)
        self.create_plan(self.plans[0])
        response = self.client.delete(support_factories.PlanFactory.get_list_url(), data=self.plans[0])
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_user_can_get_plan_by_uuid(self):
        plan = support_factories.PlanFactory()
        self.client.force_authenticate(self.user)
        response = self.client.get(support_factories.PlanFactory.get_url(plan))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def create_plan(self, plan):
        response = self.client.post(support_factories.PlanFactory.get_list_url(), data=plan)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
