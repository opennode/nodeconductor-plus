from django.core.urlresolvers import reverse
import factory
import factory.fuzzy

from nodeconductor.structure.tests import factories as structure_factories
from ..models import Plan, Order


class PlanFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = Plan

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


class OrderFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = Order

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
