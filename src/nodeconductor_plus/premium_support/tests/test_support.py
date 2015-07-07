from rest_framework import status, test

from nodeconductor.structure.tests import factories as structure_factories
from nodeconductor.structure import models as structure_models
from nodeconductor_plus.premium_support import models as support_models
from nodeconductor_plus.premium_support.tests import factories as support_factories


class SupportPlanTest(test.APITransactionTestCase):
    def setUp(self):
        self.staff = structure_factories.UserFactory(is_staff=True)
        self.user = structure_factories.UserFactory()
        self.plans = [
            {
                'name': 'Bronze support',
                'description': 'Gives you access to online documentation, community forums, and billing support.',
                'base_hours': 100,
                'hour_rate': 10
            },
            {
                'name': 'Silver support',
                'description': 'Gives you direct access to our support team.',
                'base_hours': 200,
                'hour_rate': 20
            },
            {
                'name': 'Gold support',
                'description': '24x7 phone support, rapid response times and consultation on application development.',
                'base_hours': 300,
                'hour_rate': 30
            }
        ]

    def test_staff_can_create_plan(self):
        self.client.force_authenticate(self.staff)
        for plan in self.plans:
            self.create_plan(plan)

    def test_user_can_get_plan_by_uuid(self):
        plan = support_factories.PlanFactory()
        self.client.force_authenticate(self.user)
        response = self.client.get(support_factories.PlanFactory.get_url(plan))
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def create_plan(self, plan):
        response = self.client.post(support_factories.PlanFactory.get_list_url(), data=plan)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)


class ContractCreationTest(test.APITransactionTestCase):

    def setUp(self):
        self.staff = structure_factories.UserFactory(is_staff=True)
        self.other_user = structure_factories.UserFactory()
        self.owner = structure_factories.UserFactory()

        self.plan = support_factories.PlanFactory()
        self.project = structure_factories.ProjectFactory()
        self.project.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)

    def test_customer_owner_can_create_contract_for_owned_project(self):
        self.client.force_authenticate(self.owner)
        response = self.create_contract()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual('Requested', response.data['state'])

    def test_user_can_not_create_contract_for_project_he_is_not_owner_of(self):
        self.client.force_authenticate(self.other_user)
        response = self.create_contract()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_user_can_not_create_contract_for_same_project_twice(self):
        self.client.force_authenticate(self.owner)
        response = self.create_contract()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

        response = self.create_contract()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_user_can_create_contract_for_same_project_if_all_other_contracts_are_cancelled(self):
        support_factories.ContractFactory(
            state=support_models.Contract.States.CANCELLED,
            plan=self.plan,
            project=self.project,
            user=self.owner
        )

        self.client.force_authenticate(self.owner)
        response = self.create_contract()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_other_user_can_not_see_contracts_for_project_he_is_not_owner_of(self):
        self.client.force_authenticate(self.owner)
        self.create_contract()

        self.client.force_authenticate(self.other_user)
        response = self.client.get(support_factories.ContractFactory.get_list_url())
        self.assertEqual(0, len(response.data))

    def create_contract(self):
        data = {
            'plan': support_factories.PlanFactory.get_url(self.plan),
            'project': structure_factories.ProjectFactory.get_url(self.project)
        }
        return self.client.post(support_factories.ContractFactory.get_list_url(), data=data)


class ContractStateTransitionTest(test.APITransactionTestCase):

    def setUp(self):
        self.other_user = structure_factories.UserFactory()
        self.staff = structure_factories.UserFactory(is_staff=True)
        self.owner = structure_factories.UserFactory()
        self.project = structure_factories.ProjectFactory()
        self.project.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)

        self.plan = support_factories.PlanFactory()
        self.contract = support_factories.ContractFactory(
            state=support_models.Contract.States.REQUESTED,
            plan=self.plan,
            project=self.project,
            user=self.owner
        )

    def test_user_can_cancel_contract_in_requested_or_approved_state(self):
        for state in (support_models.Contract.States.REQUESTED, support_models.Contract.States.APPROVED):
            contract = support_factories.ContractFactory(
                state=state,
                plan=self.plan,
                project=self.project,
                user=self.owner
            )

            self.client.force_authenticate(self.owner)
            response = self.client.post(support_factories.ContractFactory.get_url(contract, action='cancel'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_other_user_can_not_modify_contract(self):
        self.client.force_authenticate(self.other_user)
        response = self.client.post(support_factories.ContractFactory.get_url(self.contract, action='cancel'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_not_update_or_delete_contract(self):
        self.client.force_authenticate(self.owner)

        response = self.client.delete(support_factories.ContractFactory.get_url(self.contract))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        response = self.client.post(support_factories.ContractFactory.get_url(self.contract), data={
            'plan': support_factories.PlanFactory.get_url(self.plan),
            'project': structure_factories.ProjectFactory.get_url(self.project)
        })
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
