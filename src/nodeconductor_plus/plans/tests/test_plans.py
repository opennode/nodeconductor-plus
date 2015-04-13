from rest_framework import test, status

import factories
from nodeconductor.structure.tests import factories as structure_factories


class PlanListTest(test.APITransactionTestCase):

    def setUp(self):
        self.user = structure_factories.UserFactory()
        self.plan = factories.PlanFactory()

    def test_registered_user_can_see_plans_list(self):
        self.client.force_authenticate(self.user)
        response = self.client.get(factories.PlanFactory.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1, 'Response should contain at least one plan')
