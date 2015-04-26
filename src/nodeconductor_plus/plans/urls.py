import views


def register_in(router):
    router.register(r'plans', views.PlanViewSet)
    router.register(r'orders', views.OrderViewSet)
