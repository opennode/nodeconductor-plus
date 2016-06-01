import mock

from rest_framework import status, test

from nodeconductor.structure.tests import factories as structure_factories

from . import factories


@mock.patch('nodeconductor.structure.models.ServiceProjectLink.get_backend')
class ProjectDeletionTest(test.APITransactionTestCase):
    def setUp(self):
        self.admin = structure_factories.UserFactory(is_staff=True)

    def test_when_synced_project_deleted_view_calls_backend(self, mock_backend):
        project = factories.GitLabProjectFactory(backend_id='valid_backend_id')

        self.client.force_authenticate(user=self.admin)
        url = factories.GitLabProjectFactory.get_url(project)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_backend().destroy.assert_called_with(project, force=False)

    def test_when_project_is_not_synced_backend_is_not_called(self, mock_backend):
        project = factories.GitLabProjectFactory(backend_id='')

        self.client.force_authenticate(user=self.admin)
        url = factories.GitLabProjectFactory.get_url(project)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(mock_backend().destroy.called)


@mock.patch('nodeconductor.structure.models.ServiceProjectLink.get_backend')
class GroupCreationTest(test.APITransactionTestCase):
    def setUp(self):
        self.staff = structure_factories.UserFactory(is_staff=True)
        self.spl = factories.GitLabServiceProjectLinkFactory()
        self.valid_data = {
            'path': 'test-group',
            'name': 'Test Group',
            'service_project_link': factories.GitLabServiceProjectLinkFactory.get_url(self.spl),
        }

    def test_group_cannot_be_created_if_group_with_such_path_already_exist(self, mock_backend):
        self.client.force_authenticate(user=self.staff)
        url = factories.GitLabGroupFactory.get_list_url()
        factories.GitLabGroupFactory(path=self.valid_data['path'], service_project_link=self.spl)

        response = self.client.post(url, self.valid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


@mock.patch('nodeconductor.structure.models.ServiceProjectLink.get_backend')
class GroupDeletionTest(test.APITransactionTestCase):
    def setUp(self):
        self.admin = structure_factories.UserFactory(is_staff=True)

    def test_when_group_deleted_view_calls_backend(self, mock_backend):
        group = factories.GitLabGroupFactory(backend_id='valid_backend_id')

        self.client.force_authenticate(user=self.admin)
        url = factories.GitLabGroupFactory.get_url(group)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        mock_backend().destroy.assert_called_with(group, force=False)

    def test_when_group_is_not_synced_backend_is_not_called(self, mock_backend):
        group = factories.GitLabGroupFactory(backend_id='')

        self.client.force_authenticate(user=self.admin)
        url = factories.GitLabGroupFactory.get_url(group)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(mock_backend().destroy.called)

    def test_if_group_has_project_deletion_is_not_allowed(self, mock_backend):
        group = factories.GitLabGroupFactory()
        factories.GitLabProjectFactory(group=group)

        self.client.force_authenticate(user=self.admin)
        url = factories.GitLabGroupFactory.get_url(group)
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
