from nodeconductor_plus.digitalocean import views


def register_in(router):
    router.register(r'digitalocean', views.ServiceViewSet, base_name='digitalocean')
    router.register(r'digitalocean-images', views.ImageViewSet, base_name='digitalocean-image')
