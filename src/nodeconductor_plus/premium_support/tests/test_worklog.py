from rest_framework import status, test

from nodeconductor.structure.tests import factories as structure_factories
from nodeconductor_plus.premium_support import models as support_models
from nodeconductor_plus.premium_support.tests import factories as support_factories


class SupportWorklogTest(test.APITransactionTestCase):

    def setUp(self):
        self.staff = structure_factories.UserFactory(is_staff=True)
        self.user = structure_factories.UserFactory()
        self.plan = support_factories.PlanFactory()
        self.project = structure_factories.ProjectFactory()
        self.contract = support_factories.ContractFactory(
            state=support_models.Contract.States.APPROVED,
            plan=self.plan,
            project=self.project,
            user=self.user
        )
        self.support_case = support_factories.SupportCaseFactory(contract=self.contract)
        self.list_url = support_factories.WorklogFactory.get_list_url()
        self.worklog_data = {
            'support_case': support_factories.SupportCaseFactory.get_url(self.support_case),
            'time_spent': 10
        }

    def test_staff_can_create_worklog(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(self.list_url, data=self.worklog_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_user_can_not_create_worklog(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.list_url, data=self.worklog_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)
