from nodeconductor_plus.digitalocean import views


def register_in(router):
    router.register(r'digitalocean', views.ServiceViewSet, base_name='digitalocean')
    router.register(r'digitalocean-images', views.ImageViewSet, base_name='digitalocean-image')
    router.register(r'digitalocean-regions', views.RegionViewSet, base_name='digitalocean-region')
    router.register(r'digitalocean-sizes', views.SizeViewSet, base_name='digitalocean-size')
    router.register(r'digitalocean-resources', views.ResourceViewSet, base_name='digitalocean-resource')
    router.register(r'digitalocean-service-project-link', views.ServiceProjectLinkViewSet, base_name='digitalocean-spl')
