import mock
import unittest

from nodeconductor_plus.aws.tests import factories


class AWSBackendCachedMethodsTest(unittest.TestCase):
    def setUp(self):
        self.mocked_backend = mock.Mock()
        self.aws_service = factories.AWSServiceFactory()
        factories.RegionFactory.create_batch(2)

    def test_caching_pulled_images_from_backend(self):
        backend = self.aws_service.get_backend()
        node_driver_mock = mock.Mock()
        node_driver_mock.list_images = mock.Mock(
            return_value=factories.ImageFactory.build_batch(2)
        )
        backend._get_api = mock.Mock(return_value=node_driver_mock)

        backend.pull_images()

    def test_caching_pulled_resources_from_backend(self):
        backend = self.aws_service.get_backend()
        node_driver_mock = mock.Mock()
        node_driver_mock.list_nodes = mock.Mock(
            return_value=factories.ImageFactory.build_batch(2)
        )
        backend._get_api = mock.Mock(return_value=node_driver_mock)

        backend.get_managed_resources()
