from . import views


def register_in(router):
    router.register(r'plans', views.PlanViewSet)
    router.register(r'plan-customers', views.PlanCustomerViewSet, base_name='plan_customer')
