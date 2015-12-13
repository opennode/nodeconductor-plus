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
    backend_id = 'test_backend_id'

    @classmethod
    def get_url(self, plan=None):
        if plan is None:
            plan = PlanFactory()
        return 'http://testserver' + reverse('plan-detail', kwargs={'uuid': plan.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('plan-list')


class AgreementFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Agreement

    plan = factory.SubFactory(PlanFactory)
    customer = factory.SubFactory(structure_factories.CustomerFactory)
    user = factory.SubFactory(structure_factories.UserFactory)
    backend_id = factory.Sequence(lambda n: 'AGREEMENT_ID%s' % n)
    token = factory.Sequence(lambda n: 'TOKEN%s' % n)

    @classmethod
    def get_url(self, agreement=None):
        if agreement is None:
            agreement = AgreementFactory()
        return 'http://testserver' + reverse('agreement-detail', kwargs={'uuid': agreement.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('agreement-list')
