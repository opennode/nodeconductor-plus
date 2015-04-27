from django.conf import settings
from rest_framework import test, status

import factories
from .. import models
from nodeconductor.structure import models as structure_models
from nodeconductor.structure.tests import factories as structure_factories


class OrderListTest(test.APITransactionTestCase):

    def setUp(self):
        self.customer = structure_factories.CustomerFactory()
        self.owner = structure_factories.UserFactory()
        self.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)
        self.staff = structure_factories.UserFactory(is_staff=True)
        self.plan = factories.PlanFactory()

    def test_staff_can_see_all_orders(self):
        orders = [factories.OrderFactory() for _ in range(3)]

        self.client.force_authenticate(self.staff)
        response = self.client.get(factories.OrderFactory.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertItemsEqual([o['uuid'] for o in response.data], [o.uuid.hex for o in orders])

    def test_owner_can_see_his_customer_orders(self):
        orders = [factories.OrderFactory(customer=self.customer, plan=self.plan) for _ in range(3)]

        self.client.force_authenticate(self.owner)
        response = self.client.get(factories.OrderFactory.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertItemsEqual([o['uuid'] for o in response.data], [o.uuid.hex for o in orders])

    def test_owner_cannot_see_other_customer_orders(self):
        [factories.OrderFactory(plan=self.plan) for _ in range(3)]

        self.client.force_authenticate(self.owner)
        response = self.client.get(factories.OrderFactory.get_list_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data)


class OrderCreateTest(test.APITransactionTestCase):

    def setUp(self):
        self.customer = structure_factories.CustomerFactory()
        self.owner = structure_factories.UserFactory()
        self.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)
        self.staff = structure_factories.UserFactory(is_staff=True)
        self.plan = factories.PlanFactory()

    def test_customer_owner_can_create_order_for_his_customer(self):
        data = {
            'customer': structure_factories.CustomerFactory.get_url(self.customer),
            'plan': factories.PlanFactory.get_url(self.plan),
        }

        self.client.force_authenticate(self.owner)
        response = self.client.post(factories.OrderFactory.get_list_url(), data=data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(models.Order.objects.filter(plan=self.plan, customer=self.customer, user=self.owner).exists())

    def test_customer_owner_cannot_create_order_for_not_his_customer(self):
        other_customer = structure_factories.CustomerFactory()
        data = {
            'customer': structure_factories.CustomerFactory.get_url(other_customer),
            'plan': factories.PlanFactory.get_url(self.plan),
        }

        self.client.force_authenticate(self.owner)
        response = self.client.post(factories.OrderFactory.get_list_url(), data=data)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(models.Order.objects.filter(plan=self.plan, customer=other_customer).exists())


class OrderActionsTest(test.APITransactionTestCase):

    def setUp(self):
        self.customer = structure_factories.CustomerFactory()
        self.owner = structure_factories.UserFactory()
        self.customer.add_user(self.owner, structure_models.CustomerRole.OWNER)
        self.order = factories.OrderFactory(customer=self.customer)

    def test_order_can_be_executed_manually_with_enabled_payments_dummy_mode(self):
        if hasattr(settings, 'NODECONDUCTOR'):
            settings.NODECONDUCTOR['PAYMENTS_DUMMY'] = True
        else:
            settings.NODECONDUCTOR = {'PAYMENTS_DUMMY': True}

        self.client.force_authenticate(self.owner)
        response = self.client.post(factories.OrderFactory.get_url(self.order, action='execute'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reread_order = models.Order.objects.get(pk=self.order.pk)
        self.assertEqual(reread_order.state, models.Order.States.COMPLETED)
        self.assertTrue(models.PlanCustomer.objects.filter(plan=self.order.plan, customer=self.customer).exists())

    def test_order_cannot_be_executed_manually_with_disabled_payments_dummy_mode(self):
        if hasattr(settings, 'NODECONDUCTOR'):
            settings.NODECONDUCTOR['PAYMENTS_DUMMY'] = False
        else:
            settings.NODECONDUCTOR = {'PAYMENTS_DUMMY': False}

        self.client.force_authenticate(self.owner)
        response = self.client.post(factories.OrderFactory.get_url(self.order, action='execute'))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        reread_order = models.Order.objects.get(pk=self.order.pk)
        self.assertEqual(reread_order.state, models.Order.States.PROCESSING)

    def test_not_processing_order_cannot_be_executed_with_enabled_dummy_mode(self):
        if hasattr(settings, 'NODECONDUCTOR'):
            settings.NODECONDUCTOR['PAYMENTS_DUMMY'] = True
        else:
            settings.NODECONDUCTOR = {'PAYMENTS_DUMMY': True}
        self.order.state = models.Order.States.FAILED
        self.order.save()

        self.client.force_authenticate(self.owner)
        response = self.client.post(factories.OrderFactory.get_url(self.order, action='execute'))

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        reread_order = models.Order.objects.get(pk=self.order.pk)
        self.assertEqual(reread_order.state, models.Order.States.FAILED)
