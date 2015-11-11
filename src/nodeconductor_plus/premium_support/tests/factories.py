import factory
import factory.fuzzy
from django.core.urlresolvers import reverse

from nodeconductor_plus.premium_support import models


class PlanFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Plan

    name = factory.Sequence(lambda n: 'plan%s' % n)
    description = factory.fuzzy.FuzzyText()
    base_rate = factory.fuzzy.FuzzyDecimal(100, 500)
    hour_rate = factory.fuzzy.FuzzyDecimal(0, 50)

    @classmethod
    def get_url(self, plan=None):
        if plan is None:
            plan = PlanFactory()
        return 'http://testserver' + reverse('premium-support-plan-detail', kwargs={'uuid': plan.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('premium-support-plan-list')


class ContractFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Contract

    @classmethod
    def get_url(self, contract, action=None):
        url = 'http://testserver' + reverse('premium-support-contract-detail', kwargs={'uuid': contract.uuid})
        return action and url + action + '/' or url

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('premium-support-contract-list')


class SupportCaseFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.SupportCase

    name = factory.Sequence(lambda n: 'case%s' % n)
    description = factory.fuzzy.FuzzyText()

    @classmethod
    def get_url(self, support_case):
        return 'http://testserver' + reverse('premium-support-case-detail', kwargs={'uuid': support_case.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('premium-support-case-list')


class WorklogFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Worklog

    time_spent = factory.fuzzy.FuzzyInteger(1, 20)
    description = factory.fuzzy.FuzzyText()

    @classmethod
    def get_url(self, worklog):
        return 'http://testserver' + reverse('premium-support-worklog-detail', kwargs={'uuid': worklog.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('premium-support-worklog-list')
