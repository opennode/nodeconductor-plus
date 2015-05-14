from nodeconductor_plus.digitalocean import views


def register_in(router):
    router.register(r'digitalocean', views.ServiceViewSet)
