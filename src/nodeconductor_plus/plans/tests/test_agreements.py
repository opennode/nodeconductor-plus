from mock import patch
from rest_framework import test, status

from nodeconductor.structure import models as structure_models
from nodeconductor.structure.tests import factories as structure_factories

from . import factories
from .. import models, utils


class AgreementListTest(test.APITransactionTestCase):

    def setUp(self):
        self.customer = structure_factories.CustomerFactory()
        self.owner = structure_factories.UserFactory()
        self.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)
        self.staff = structure_factories.UserFactory(is_staff=True)
        self.plan = factories.PlanFactory()
        models.Agreement.objects.all().delete()

    def test_staff_can_see_all_agreements(self):
        agreements = models.Agreement.objects.all()

        self.client.force_authenticate(self.staff)
        response = self.client.get(factories.AgreementFactory.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertItemsEqual([o['uuid'] for o in response.data], [o.uuid.hex for o in agreements])

    def test_owner_can_see_his_customer_agreements(self):
        agreements = models.Agreement.objects.filter(customer=self.customer)

        self.client.force_authenticate(self.owner)
        response = self.client.get(factories.AgreementFactory.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertItemsEqual([o['uuid'] for o in response.data], [o.uuid.hex for o in agreements])

    def test_owner_cannot_see_other_customer_agreements(self):
        [factories.AgreementFactory(plan=self.plan) for _ in range(3)]

        self.client.force_authenticate(self.owner)
        response = self.client.get(factories.AgreementFactory.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)


class AgreementCreateTest(test.APITransactionTestCase):

    def setUp(self):
        self.customer = structure_factories.CustomerFactory()
        self.owner = structure_factories.UserFactory()
        self.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)
        self.staff = structure_factories.UserFactory(is_staff=True)
        self.plan = factories.PlanFactory()
        self.return_url = 'http://example.com/approve-agreement/'
        self.cancel_url = 'http://example.com/cancel-agreement/'

    def test_customer_owner_can_create_agreement_for_his_customer(self):
        data = {
            'customer': structure_factories.CustomerFactory.get_url(self.customer),
            'plan': factories.PlanFactory.get_url(self.plan),
            'return_url': self.return_url,
            'cancel_url': self.cancel_url
        }

        response = self.create_agreement(data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertTrue(models.Agreement.objects.filter(plan=self.plan, customer=self.customer, user=self.owner).exists())

    def test_customer_owner_cannot_create_agreement_for_not_his_customer(self):
        other_customer = structure_factories.CustomerFactory()
        data = {
            'customer': structure_factories.CustomerFactory.get_url(other_customer),
            'plan': factories.PlanFactory.get_url(self.plan),
            'return_url': self.return_url,
            'cancel_url': self.cancel_url
        }

        response = self.create_agreement(data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(models.Agreement.objects.filter(plan=self.plan, customer=other_customer).exists())

    def test_agreement_cannot_be_created_without_customer(self):
        data = {
            'plan': factories.PlanFactory.get_url(self.plan),
            'return_url': self.return_url,
            'cancel_url': self.cancel_url
        }

        response = self.create_agreement(data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(models.Agreement.objects.filter(plan=self.plan, user=self.owner).exists())

    def test_agreement_cannot_be_created_without_plan(self):
        data = {
            'customer': structure_factories.CustomerFactory.get_url(self.customer),
            'return_url': self.return_url,
            'cancel_url': self.cancel_url
        }

        response = self.create_agreement(data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(models.Agreement.objects.filter(customer=self.customer, user=self.owner).exists())

    def create_agreement(self, data):
        self.client.force_authenticate(self.owner)
        with patch('nodeconductor_plus.plans.views.utils'):
            return self.client.post(factories.AgreementFactory.get_list_url(), data=data)


class AgreementCallbackViewsTest(test.APITransactionTestCase):

    def setUp(self):
        self.customer = structure_factories.CustomerFactory()
        self.owner = structure_factories.UserFactory()
        self.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)
        self.other = structure_factories.UserFactory()
        self.plan = factories.PlanFactory()

    def check_action_result(self, user, action, state):
        models.Agreement.objects.all().delete()
        token = 'VALID_TOKEN'
        self.agreement = models.Agreement.objects.create(
            plan=self.plan, state=models.Agreement.States.PENDING, token=token, customer=self.customer)

        self.client.force_authenticate(user)
        url = factories.AgreementFactory.get_list_url() + action + '/'
        self.client.post(url, {'token': token})

        self.agreement.refresh_from_db()
        self.assertEqual(self.agreement.state, state)

    def test_owner_can_approve_payment(self):
        with patch('nodeconductor_plus.plans.utils.activate_agreement') as mocked_activate_agreement:
            self.check_action_result(self.owner, 'approve', models.Agreement.States.APPROVED)
            mocked_activate_agreement.assert_called_with(self.agreement)

    def test_owner_can_cancel_payment(self):
        self.check_action_result(self.owner, 'cancel', models.Agreement.States.CANCELLED)

    def test_other_user_can_not_approve_payment(self):
        self.check_action_result(self.other, 'approve', models.Agreement.States.PENDING)

    def test_other_user_can_not_cancel_payment(self):
        self.check_action_result(self.other, 'cancel', models.Agreement.States.PENDING)


@patch('nodeconductor_plus.plans.utils.PaypalBackend')
class AgreementBillingTasksTest(test.APITransactionTestCase):
    def test_cancel_agreement_task_calls_billing(self, mocked_billing):
        agreement = factories.AgreementFactory(state=models.Agreement.States.ACTIVE)
        utils.cancel_agreement(agreement)
        mocked_billing().cancel_agreement.assert_called_with(agreement.backend_id)

        agreement = models.Agreement.objects.get(pk=agreement.pk)
        self.assertEqual(agreement.state, models.Agreement.States.CANCELLED)

    def test_activate_agreement_task_calls_billing(self, mocked_billing):
        agreement = factories.AgreementFactory(state=models.Agreement.States.APPROVED)
        mocked_billing().execute_agreement.return_value = 'VALID_ID'
        utils.activate_agreement(agreement)
        mocked_billing().execute_agreement.assert_called_with(agreement.token)

        agreement = models.Agreement.objects.get(pk=agreement.pk)
        self.assertEqual(agreement.state, models.Agreement.States.ACTIVE)
