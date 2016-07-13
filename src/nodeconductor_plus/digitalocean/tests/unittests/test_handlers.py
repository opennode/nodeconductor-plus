from django.test import TestCase
from mock import patch
from permission.utils.autodiscover import autodiscover

from nodeconductor.core import utils as core_utils
from nodeconductor.structure import models as structure_models
from nodeconductor.structure.tests import factories as structure_factories

from .. import factories
from ... import models


@patch('nodeconductor.core.tasks.IndependentBackendMethodTask.delay')
class SshKeysHandlersTest(TestCase):

    def setUp(self):
        autodiscover()  # permissions could be not discovered in unittests
        self.user = structure_factories.UserFactory()
        self.ssh_key = structure_factories.SshPublicKeyFactory(user=self.user)
        self.service = factories.DigitalOceanServiceFactory()

    def test_ssh_key_will_be_removed_if_user_lost_connection_to_service_settings(self, mocked_task_call):
        project = structure_factories.ProjectFactory(customer=self.service.customer)
        project.add_user(self.user, structure_models.ProjectRole.ADMINISTRATOR)
        project.remove_user(self.user)

        serialized_settings = core_utils.serialize_instance(self.service.settings)
        mocked_task_call.assert_called_once_with(
            serialized_settings, 'remove_ssh_key', self.ssh_key.name, self.ssh_key.fingerprint)

    def test_ssh_key_will_not_be_removed_if_user_still_has_connection_to_service_settings(self, mocked_task_call):
        project = structure_factories.ProjectFactory(customer=self.service.customer)
        project.add_user(self.user, structure_models.ProjectRole.ADMINISTRATOR)
        self.service.customer.add_user(self.user, structure_models.CustomerRole.OWNER)
        project.remove_user(self.user)

        self.assertEqual(mocked_task_call.call_count, 0)

    def test_ssh_key_will_be_deleted_from_service_settings_on_user_deletion(self, mocked_task_call):
        self.service.customer.add_user(self.user, structure_models.CustomerRole.OWNER)
        self.user.delete()

        serialized_tenant = core_utils.serialize_instance(self.service.settings)
        mocked_task_call.assert_called_once_with(
            serialized_tenant, 'remove_ssh_key', self.ssh_key.name, self.ssh_key.fingerprint)

    def test_ssh_key_will_be_deleted_from_service_settings_on_ssh_key_deletion(self, mocked_task_call):
        self.service.customer.add_user(self.user, structure_models.CustomerRole.OWNER)
        self.ssh_key.delete()

        serialized_tenant = core_utils.serialize_instance(self.service.settings)
        mocked_task_call.assert_called_once_with(
            serialized_tenant, 'remove_ssh_key', self.ssh_key.name, self.ssh_key.fingerprint)
