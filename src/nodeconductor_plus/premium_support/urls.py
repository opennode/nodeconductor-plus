from nodeconductor_plus.premium_support import views


def register_in(router):
    router.register(r'premium-support-plans', views.PlanViewSet, base_name='premium-support-plan')
    router.register(r'premium-support-contracts', views.SupportContractViewSet, base_name='premium-support-contract')
    router.register(r'premium-support-cases', views.SupportCaseViewSet, base_name='premium-support-case')
    router.register(r'premium-support-worklogs', views.SupportWorklogViewSet, base_name='premium-support-worklog')
