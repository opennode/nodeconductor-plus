from nodeconductor_plus.premium_support import views


def register_in(router):
    router.register(r'premium-support-plans', views.PlanViewSet, base_name='premium-support-plan')
    router.register(r'premium-support-contracts', views.ContractViewSet, base_name='premium-support-contract')
