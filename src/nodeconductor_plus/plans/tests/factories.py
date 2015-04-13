from django.core.urlresolvers import reverse
import factory
import factory.fuzzy

from ..models import Plan


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
