import logging
from rest_framework import status, test

from nodeconductor.structure.tests import factories as structure_factories
from nodeconductor.structure import models as structure_models
from nodeconductor_plus.premium_support import models as support_models
from nodeconductor_plus.premium_support.tests import factories as support_factories


class SupportContractCreationTest(test.APITransactionTestCase):

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
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, response.data)

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

    def test_user_can_filter_contract_by_project(self):
        """
        Create two projects with contracts.
        After filtering contract by project only one of them is returned.
        """
        support_factories.ContractFactory(
            plan=self.plan,
            project=self.project,
            user=self.owner
        )

        other_project = structure_factories.ProjectFactory()
        other_project.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)

        support_factories.ContractFactory(
            plan=self.plan,
            project=other_project,
            user=self.owner
        )

        self.client.force_authenticate(self.owner)
        response = self.client.get(support_factories.ContractFactory.get_list_url(),
                data={'project_uuid': other_project.uuid.hex})
        self.assertEqual(1, len(response.data))


    def create_contract(self):
        data = {
            'plan': support_factories.PlanFactory.get_url(self.plan),
            'project': structure_factories.ProjectFactory.get_url(self.project)
        }
        return self.client.post(support_factories.ContractFactory.get_list_url(), data=data)


class SupportContractStateTransitionTest(test.APITransactionTestCase):

    def setUp(self):
        self.other_user = structure_factories.UserFactory()
        self.support_admin = structure_factories.UserFactory(is_staff=True)
        self.owner = structure_factories.UserFactory()
        self.project = structure_factories.ProjectFactory()
        self.project.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)

        self.plan = support_factories.PlanFactory()
        self.contract = support_factories.ContractFactory(
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

            response = self.client.get(support_factories.ContractFactory.get_url(contract))
            self.assertEqual('Cancelled', response.data['state'], response.data)

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

    def test_support_admin_can_approve_contract(self):
        self.client.force_authenticate(self.support_admin)
        response = self.client.post(support_factories.ContractFactory.get_url(self.contract, action='approve'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(support_factories.ContractFactory.get_url(self.contract))
        self.assertEqual('Approved', response.data['state'], response.data)

    def test_user_can_not_approve_contract(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(support_factories.ContractFactory.get_url(self.contract, action='approve'))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_support_admin_can_not_approve_cancelled_contract(self):
        self.contract.state = support_models.Contract.States.CANCELLED
        self.contract.save()

        self.client.force_authenticate(self.support_admin)
        response = self.client.post(support_factories.ContractFactory.get_url(self.contract, action='approve'))
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
