import factory

from django.core.urlresolvers import reverse

from nodeconductor.structure.tests import factories as structure_factories

from .. import models


class DigitalOceanServiceFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.DigitalOceanService

    name = factory.Sequence(lambda n: 'service%s' % n)
    settings = factory.SubFactory(structure_factories.ServiceSettingsFactory)
    customer = factory.SubFactory(structure_factories.CustomerFactory)

    @classmethod
    def get_url(self, service=None):
        if service is None:
            service = DigitalOceanServiceFactory()
        return 'http://testserver' + reverse('digitalocean-detail', kwargs={'uuid': service.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('digitalocean-list')


class DigitalOceanServiceProjectLingFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.DigitalOceanServiceProjectLink

    service = factory.SubFactory(DigitalOceanServiceFactory)
    project = factory.SubFactory(structure_factories.ProjectFactory)


class RegionFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Region

    name = factory.Sequence(lambda n: 'region%s' % n)


class ImageFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Image

    name = factory.Sequence(lambda n: 'image%s' % n)
    backend_id = factory.Sequence(lambda n: 'image-id%s' % n)

    @classmethod
    def get_url(cls, image=None):
        if image is None:
            image = ImageFactory()
        return 'http://testserver' + reverse('digitalocean-image-detail', kwargs={'uuid': image.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('digitalocean-image-list')


class SizeFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Size

    name = factory.Sequence(lambda n: 'size%s' % n)
    backend_id = factory.Sequence(lambda n: 'size-id%s' % n)

    cores = 2
    ram = 2 * 1024
    disk = 10 * 1024
    transfer = 10 * 1024 * 1024
