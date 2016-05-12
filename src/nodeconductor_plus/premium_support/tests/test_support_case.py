from rest_framework import status, test

from nodeconductor.structure.tests import factories as structure_factories
from nodeconductor.structure import models as structure_models
from nodeconductor_plus.premium_support import models as support_models
from nodeconductor_plus.premium_support.tests import factories as support_factories


class SupportCaseTest(test.APITransactionTestCase):
    def setUp(self):
        self.other_user = structure_factories.UserFactory()
        self.staff = structure_factories.UserFactory(is_staff=True)
        self.plan = support_factories.PlanFactory()

        self.owner = structure_factories.UserFactory()
        self.project = structure_factories.ProjectFactory()
        self.project.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)

        self.contract = support_factories.ContractFactory(
            state=support_models.Contract.States.APPROVED,
            plan=self.plan,
            project=self.project
        )

        self.contract_url = support_factories.ContractFactory.get_url(self.contract)

        self.support_case = {
            'contract': self.contract_url,
            'name': 'Support case'
        }

        self.url = support_factories.SupportCaseFactory.get_list_url()

    def test_user_can_create_support_case_for_approved_contract(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.url, data=self.support_case)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_user_can_not_create_support_case_for_requested_or_cancelled_contract(self):
        self.client.force_authenticate(self.owner)
        invalid_states = (support_models.Contract.States.REQUESTED, support_models.Contract.States.CANCELLED)
        for state in invalid_states:
            self.contract.state = state
            self.contract.save()

            response = self.client.post(self.url, data=self.support_case)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

    def test_other_user_can_not_see_support_case_for_project_he_is_not_owner_of(self):
        self.client.force_authenticate(self.other_user)
        support_case = support_factories.SupportCaseFactory(contract=self.contract)
        response = self.client.get(support_factories.SupportCaseFactory.get_url(support_case))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_not_update_contract_of_support_case(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.url, data=self.support_case)

        other_contract = support_factories.ContractFactory(
            state=support_models.Contract.States.CANCELLED,
            plan=self.plan,
            project=self.project
        )
        new_data = {'contract': support_factories.ContractFactory.get_url(other_contract)}
        response = self.client.patch(response.data['url'], data=new_data)
        self.assertEqual(response.data['contract'], self.contract_url)

    def test_user_can_update_name_and_description_of_support_case(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(self.url, data=self.support_case)
        url = response.data['url']

        new_data = {'name': 'New name', 'description': 'New description'}
        response = self.client.patch(url, data=new_data)
        self.assertEqual(response.data['name'], new_data['name'])
        self.assertEqual(response.data['description'], new_data['description'])

    def test_user_can_specify_optional_resource_for_support_case(self):
        from nodeconductor_plus.gitlab.tests.factories import GitLabProjectFactory

        self.support_case['resource'] = InstanceFactory.get_url()
        self.client.force_authenticate(self.staff)
        response = self.client.post(self.url, data=self.support_case)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)

    def test_user_can_filter_support_case_by_contract(self):
        """
        Create one case for each of contracts.
        After filtering by contract only one case is returned.
        """
        support_case = support_factories.SupportCaseFactory(contract=self.contract)

        other_contract = support_factories.ContractFactory(
            state=support_models.Contract.States.CANCELLED,
            plan=self.plan,
            project=self.project
        )
        other_case = support_factories.SupportCaseFactory(contract=other_contract)

        self.client.force_authenticate(self.owner)
        response = self.client.get(self.url, data={'contract_uuid': other_contract.uuid.hex})
        self.assertEqual(1, len(response.data))
