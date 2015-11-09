from mock import patch

from django.core.urlresolvers import reverse
from rest_framework import status, test

from nodeconductor.structure import SupportedServices
from nodeconductor.structure.models import CustomerRole
from nodeconductor.structure.tests import factories as structure_factories

from nodeconductor_plus.digitalocean.models import Image, DigitalOceanService
from nodeconductor_plus.digitalocean.tasks import provision
from nodeconductor_plus.digitalocean.tests import factories


class DropletProvisionTest(test.APITransactionTestCase):
    # def setUp(self):
    #     self.customer = structure_factories.CustomerFactory()
    #     self.user = structure_factories.UserFactory()
    #     self.customer.add_user(self.user, CustomerRole.OWNER)
    #     self.project = structure_factories.ProjectFactory(customer=self.customer)

    #     self.settings = structure_factories.ServiceSettingsFactory(
    #         type=SupportedServices.Types.DigitalOcean)
    #     self.region = factories.RegionFactory(settings=self.settings)

    #     self.image = factories.ImageFactory(settings=self.settings)
    #     self.image.regions.add(self.region)

    #     self.size = factories.SizeFactory(settings=self.settings)
    #     self.size.regions.add(self.region)

    #     self.service = factories.DigitalOceanServiceFactory(
    #         settings=self.settings, customer=self.customer)
    #     self.link = factories.DigitalOceanServiceProjectLinkFactory(
    #         service=self.service, project=self.project)

    # def test_user_can_provision_droplet(self):
    #     self.client.force_authenticate(user=self.user)
    #     droplet_url = reverse('digitalocean-droplet-list')

    #     with patch('celery.app.base.Celery.send_task') as mocked:
    #         response = self.client.post(droplet_url, self._get_valid_payload())
    #         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #         mocked.assert_called_once_with('nodeconductor.digitalocean.provision', 
    #           (response.data['uuid'],),
    #           {'backend_region_id': self.region.backend_id,
    #           'backend_size_id': self.size.backend_id,
    #           'backend_image_id': self.image.backend_id,
    #           'ssh_key_uuid': None}, countdown=2)

    # def test_provision_task(self):
    #     droplet = factories.DropletFactory()
    #     kwargs = {
    #         'backend_region_id': self.region.backend_id,
    #         'backend_image_id': self.image.backend_id,
    #         'backend_size_id': self.size.backend_id
    #     }
    #     with patch('nodeconductor_plus.digitalocean.tasks.provision_droplet') as mocked_provision_droplet:
    #         with patch('nodeconductor_plus.digitalocean.tasks.sync_service_project_links') as mocked_sync:
    #             provision.delay(droplet.uuid.hex, **kwargs)
    #             mocked_sync.si.assert_called_once_with(droplet.service_project_link.to_string(), initial=True)
    #             mocked_provision_droplet.s.assert_called_once_with(droplet.uuid.hex, **kwargs)

    # def _get_valid_payload(self):
    #     return {
    #         'name': 'Dummy Droplet',
    #         'service_project_link': factories.DigitalOceanServiceProjectLinkFactory.get_url(self.link),
    #         'region': factories.RegionFactory.get_url(self.region),
    #         'image': factories.ImageFactory.get_url(self.image),
    #         'size': factories.SizeFactory.get_url(self.size)
    #     }

    def test_unique(self):
        factories.ImageFactory(settings=None, backend_id=1)
        factories.ImageFactory(settings=None, backend_id=1)
        self.assertEqual(1, Image.objects.count())
