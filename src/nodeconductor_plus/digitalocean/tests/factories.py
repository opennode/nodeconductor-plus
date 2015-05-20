import factory

from django.core.urlresolvers import reverse

from nodeconductor.structure.tests import factories as structure_factories

from .. import models


class DigitalOceanServiceFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.DigitalOceanService

    name = factory.Sequence(lambda n: 'service%s' % n)
    customer = factory.SubFactory(structure_factories.CustomerFactory)
    auth_token = 'qwerty'

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
    service = factory.SubFactory(DigitalOceanServiceFactory)


class ImageFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Image

    name = factory.Sequence(lambda n: 'image%s' % n)
    service = factory.SubFactory(DigitalOceanServiceFactory)
    backend_id = factory.Sequence(lambda n: 'image-id%s' % n)

    @classmethod
    def get_url(cls, image=None):
        if image is None:
            image = ImageFactory()
        return 'http://testserver' + reverse('digitalocean-image-detail', kwargs={'uuid': image.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('digitalocean-image-list')
