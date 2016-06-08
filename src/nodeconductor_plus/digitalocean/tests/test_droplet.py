from rest_framework import status, test

from nodeconductor.structure.models import CustomerRole
from nodeconductor.structure.tests import factories as structure_factories

from .. import models
from . import factories


class DropletResizeTest(test.APITransactionTestCase):
    def setUp(self):
        self.user = structure_factories.UserFactory()
        self.customer = structure_factories.CustomerFactory()
        self.project = structure_factories.ProjectFactory(customer=self.customer)
        self.service = factories.DigitalOceanServiceFactory(customer=self.customer)
        self.customer.add_user(self.user, CustomerRole.OWNER)
        self.spl = factories.DigitalOceanServiceProjectLinkFactory(service=self.service, project=self.project)

    def test_user_can_not_resize_provisioning_droplet(self):
        self.client.force_authenticate(user=self.user)

        self.droplet = factories.DropletFactory(service_project_link=self.spl,
                                                cores=2, ram=2 * 1024, disk=10 * 1024,
                                                state=models.Droplet.States.UPDATING)
        new_size = factories.SizeFactory(cores=3, ram=3 * 1024, disk=20 * 1024)

        response = self.client.post(factories.DropletFactory.get_url(self.droplet, 'resize'), {
            'size': factories.SizeFactory.get_url(new_size),
            'disk': True
        })
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_user_can_resize_droplet_to_bigger_size(self):
        self.client.force_authenticate(user=self.user)

        self.droplet = factories.DropletFactory(service_project_link=self.spl,
                                                cores=2, ram=2 * 1024, disk=10 * 1024,
                                                state=models.Droplet.States.OK,
                                                runtime_state=models.Droplet.RuntimeStates.OFFLINE)
        new_size = factories.SizeFactory(cores=3, ram=3 * 1024, disk=20 * 1024)

        response = self.client.post(factories.DropletFactory.get_url(self.droplet, 'resize'), {
            'size': factories.SizeFactory.get_url(new_size),
            'disk': True
        })
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_user_can_resize_droplet_to_smaller_cpu(self):
        self.client.force_authenticate(user=self.user)

        self.droplet = factories.DropletFactory(service_project_link=self.spl, cores=3, disk=20 * 1024,
                                                state=models.Droplet.States.OK,
                                                runtime_state=models.Droplet.RuntimeStates.OFFLINE)
        new_size = factories.SizeFactory(cores=2, disk=20 * 1024)

        response = self.client.post(factories.DropletFactory.get_url(self.droplet, 'resize'), {
            'size': factories.SizeFactory.get_url(new_size),
            'disk': False
        })
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_user_can_not_resize_droplet_to_smaller_disk(self):
        self.client.force_authenticate(user=self.user)

        self.droplet = factories.DropletFactory(service_project_link=self.spl, disk=20 * 1024,
                                                state=models.Droplet.States.OK,
                                                runtime_state=models.Droplet.RuntimeStates.OFFLINE)
        new_size = factories.SizeFactory(disk=10 * 1024)

        response = self.client.post(factories.DropletFactory.get_url(self.droplet, 'resize'), {
            'size': factories.SizeFactory.get_url(new_size),
            'disk': True
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)

