from django.core.urlresolvers import reverse
import factory
import factory.fuzzy

from .. import models
from nodeconductor.structure.tests import factories as structure_factories


class PlanFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Plan

    name = factory.Sequence(lambda n: 'plan%s' % n)
    price = factory.fuzzy.FuzzyFloat(0, 20000)

    @classmethod
    def get_url(self, plan=None):
        if plan is None:
            plan = PlanFactory()
        return 'http://testserver' + reverse('plan-detail', kwargs={'uuid': plan.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('plan-list')


class PlanCustomerFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.PlanCustomer

    plan = factory.SubFactory(PlanFactory)
    customer = factory.SubFactory(structure_factories.CustomerFactory)

    @classmethod
    def get_url(self, plan_customer=None):
        if plan_customer is None:
            plan_customer = PlanCustomerFactory()
        return 'http://testserver' + reverse('plan_customer-detail', kwargs={'uuid': plan_customer.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('plan_customer-list')


class OrderFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Order

    plan = factory.SubFactory(PlanFactory)
    customer = factory.SubFactory(structure_factories.CustomerFactory)
    user = factory.SubFactory(structure_factories.UserFactory)

    @classmethod
    def get_url(self, order=None, action=None):
        if order is None:
            order = OrderFactory()
        url = 'http://testserver' + reverse('order-detail', kwargs={'uuid': order.uuid})
        return url if action is None else url + action + '/'

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('order-list')
