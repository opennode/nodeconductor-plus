from rest_framework import status, test

from nodeconductor.core.models import SynchronizationStates
from nodeconductor.structure.models import ProjectRole, CustomerRole, ProjectGroupRole
from nodeconductor.structure.tests import factories as structure_factories

from . import factories
from ..models import DigitalOceanService


class ServicePermissionTest(test.APITransactionTestCase):
    def setUp(self):
        self.customers = {
            'owned': structure_factories.CustomerFactory(),
            'has_admined_project': structure_factories.CustomerFactory(),
            'has_managed_project': structure_factories.CustomerFactory(),
            'has_managed_by_group_manager': structure_factories.CustomerFactory(),
        }

        self.users = {
            'customer_owner': structure_factories.UserFactory(),
            'project_admin': structure_factories.UserFactory(),
            'project_manager': structure_factories.UserFactory(),
            'group_manager': structure_factories.UserFactory(),
            'no_role': structure_factories.UserFactory(),
        }

        self.projects = {
            'owned': structure_factories.ProjectFactory(customer=self.customers['owned']),
            'admined': structure_factories.ProjectFactory(customer=self.customers['has_admined_project']),
            'managed': structure_factories.ProjectFactory(customer=self.customers['has_managed_project']),
            'managed_by_group_manager': structure_factories.ProjectFactory(
                customer=self.customers['has_managed_by_group_manager']),
        }

        self.services = {
            'owned': factories.DigitalOceanServiceFactory(
                state=SynchronizationStates.IN_SYNC, customer=self.customers['owned']),
            'admined': factories.DigitalOceanServiceFactory(
                state=SynchronizationStates.IN_SYNC, customer=self.customers['has_admined_project']),
            'managed': factories.DigitalOceanServiceFactory(
                state=SynchronizationStates.IN_SYNC, customer=self.customers['has_managed_project']),
            'managed_by_group_manager': factories.DigitalOceanServiceFactory(
                state=SynchronizationStates.IN_SYNC, customer=self.customers['has_managed_by_group_manager']),
            'not_in_project': factories.DigitalOceanServiceFactory(),
        }

        self.customers['owned'].add_user(self.users['customer_owner'], CustomerRole.OWNER)

        self.projects['admined'].add_user(self.users['project_admin'], ProjectRole.ADMINISTRATOR)
        self.projects['managed'].add_user(self.users['project_manager'], ProjectRole.MANAGER)
        project_group = structure_factories.ProjectGroupFactory()
        project_group.projects.add(self.projects['managed_by_group_manager'])
        project_group.add_user(self.users['group_manager'], ProjectGroupRole.MANAGER)

        factories.DigitalOceanServiceProjectLingFactory(service=self.services['admined'], project=self.projects['admined'])
        factories.DigitalOceanServiceProjectLingFactory(service=self.services['managed'], project=self.projects['managed'])
        factories.DigitalOceanServiceProjectLingFactory(
            service=self.services['managed_by_group_manager'], project=self.projects['managed_by_group_manager'])

    # List filtration tests
    def test_anonymous_user_cannot_list_services(self):
        response = self.client.get(factories.DigitalOceanServiceFactory.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_list_services_of_projects_he_is_administrator_of(self):
        self.client.force_authenticate(user=self.users['project_admin'])

        response = self.client.get(factories.DigitalOceanServiceFactory.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        service_url = factories.DigitalOceanServiceFactory.get_url(self.services['admined'])
        self.assertIn(service_url, [instance['url'] for instance in response.data])

    def test_user_can_list_services_of_projects_he_is_manager_of(self):
        self.client.force_authenticate(user=self.users['project_manager'])

        response = self.client.get(factories.DigitalOceanServiceFactory.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        service_url = factories.DigitalOceanServiceFactory.get_url(self.services['managed'])
        self.assertIn(service_url, [instance['url'] for instance in response.data])

    def test_user_can_list_services_of_projects_he_is_group_manager_of(self):
        self.client.force_authenticate(user=self.users['group_manager'])

        response = self.client.get(factories.DigitalOceanServiceFactory.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        service_url = factories.DigitalOceanServiceFactory.get_url(self.services['managed_by_group_manager'])
        self.assertIn(service_url, [instance['url'] for instance in response.data])

    def test_user_can_list_services_of_projects_he_is_customer_owner_of(self):
        self.client.force_authenticate(user=self.users['customer_owner'])

        response = self.client.get(factories.DigitalOceanServiceFactory.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        service_url = factories.DigitalOceanServiceFactory.get_url(self.services['owned'])
        self.assertIn(service_url, [instance['url'] for instance in response.data])

    def test_user_cannot_list_services_of_projects_he_has_no_role_in(self):
        self.client.force_authenticate(user=self.users['no_role'])

        response = self.client.get(factories.DigitalOceanServiceFactory.get_list_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for service_type in 'admined', 'managed', 'managed_by_group_manager':
            service_url = factories.DigitalOceanServiceFactory.get_url(self.services[service_type])
            self.assertNotIn(
                service_url,
                [instance['url'] for instance in response.data],
                'User (role=none) should not see service (type=' + service_type + ')',
            )

    # Direct instance access tests
    def test_anonymous_user_cannot_access_service(self):
        for service_type in 'admined', 'managed', 'not_in_project':
            response = self.client.get(factories.DigitalOceanServiceFactory.get_url(self.services[service_type]))
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_can_access_service_allowed_for_project_he_is_administrator_of(self):
        self.client.force_authenticate(user=self.users['project_admin'])

        response = self.client.get(factories.DigitalOceanServiceFactory.get_url(self.services['admined']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_access_service_allowed_for_project_he_is_manager_of(self):
        self.client.force_authenticate(user=self.users['project_manager'])

        response = self.client.get(factories.DigitalOceanServiceFactory.get_url(self.services['managed']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_access_service_allowed_for_project_he_is_group_manager_of(self):
        self.client.force_authenticate(user=self.users['group_manager'])

        response = self.client.get(factories.DigitalOceanServiceFactory.get_url(self.services['managed_by_group_manager']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_see_services_customer_name(self):
        self.client.force_authenticate(user=self.users['project_admin'])

        response = self.client.get(factories.DigitalOceanServiceFactory.get_url(self.services['admined']))

        customer = self.services['admined'].customer

        self.assertIn('customer', response.data)
        self.assertEqual(structure_factories.CustomerFactory.get_url(customer), response.data['customer'])

        self.assertIn('customer_name', response.data)
        self.assertEqual(customer.name, response.data['customer_name'])

    def test_user_cannot_access_service_allowed_for_project_he_has_no_role_in(self):
        self.client.force_authenticate(user=self.users['no_role'])

        for service_type in 'admined', 'managed':
            response = self.client.get(factories.DigitalOceanServiceFactory.get_url(self.services[service_type]))
            # 404 is used instead of 403 to hide the fact that the resource exists at all
            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND,
                'User (role=none) should not see service (type=' + service_type + ')',
            )

    def test_user_cannot_access_service_not_allowed_for_any_project(self):
        for user_role in 'customer_owner', 'project_admin', 'project_manager', 'group_manager':
            self.client.force_authenticate(user=self.users[user_role])

            response = self.client.get(factories.DigitalOceanServiceFactory.get_url(self.services['not_in_project']))
            # 404 is used instead of 403 to hide the fact that the resource exists at all
            self.assertEqual(
                response.status_code,
                status.HTTP_404_NOT_FOUND,
                'User (role=' + user_role + ') should not see service (type=not_in_project)',
            )

    # Nested objects filtration tests
    def test_user_can_see_images_within_service(self):
        for user_role, service_type in {
            'project_admin': 'admined',
            'project_manager': 'managed',
            'group_manager': 'managed_by_group_manager',
        }.iteritems():
            self.client.force_authenticate(user=self.users[user_role])

            seen_image = factories.ImageFactory(service=self.services[service_type])

            response = self.client.get(factories.DigitalOceanServiceFactory.get_url(self.services[service_type]))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

            self.assertIn(
                'images',
                response.data,
                'Cloud (type=' + service_type + ') must contain image list',
            )

            image_urls = set([image['url'] for image in response.data['images']])
            self.assertIn(
                factories.ImageFactory.get_url(seen_image),
                image_urls,
                'User (role=' + user_role + ') should see image',
            )

    # Creation tests
    def test_user_can_add_service_to_the_customer_he_owns(self):
        self.client.force_authenticate(user=self.users['customer_owner'])

        new_service = factories.DigitalOceanServiceFactory.build(customer=self.customers['owned'])
        response = self.client.post(factories.DigitalOceanServiceFactory.get_list_url(), self._get_valid_payload(new_service))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_cannot_add_service_to_the_customer_he_sees_but_doesnt_own(self):
        for user_role, customer_type in {
                'project_admin': 'has_admined_project',
                'project_manager': 'has_managed_project',
                }.items():
            self.client.force_authenticate(user=self.users[user_role])

            new_service = factories.DigitalOceanServiceFactory.build(customer=self.customers[customer_type])
            response = self.client.post(factories.DigitalOceanServiceFactory.get_list_url(), self._get_valid_payload(new_service))
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_add_service_to_the_customer_he_has_no_role_in(self):
        self.client.force_authenticate(user=self.users['no_role'])

        new_service = factories.DigitalOceanServiceFactory.build(customer=self.customers['owned'])
        response = self.client.post(factories.DigitalOceanServiceFactory.get_list_url(), self._get_valid_payload(new_service))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # Mutation tests
    def test_user_cannot_change_auth_token_of_service_he_owns(self):
        self.client.force_authenticate(user=self.users['customer_owner'])

        service = self.services['owned']

        payload = {'auth_token': 'abrakadabra'}
        response = self.client.patch(factories.DigitalOceanServiceFactory.get_url(service),
                                     data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        reread_service = DigitalOceanService.objects.get(pk=service.pk)
        self.assertEqual(reread_service.auth_token, service.auth_token)

    def test_user_cannot_change_customer_of_service_he_owns(self):
        user = self.users['customer_owner']

        self.client.force_authenticate(user=user)

        service = self.services['owned']

        new_customer = structure_factories.CustomerFactory()
        new_customer.add_user(user, CustomerRole.OWNER)

        payload = {'customer': structure_factories.CustomerFactory.get_url(new_customer)}
        response = self.client.patch(factories.DigitalOceanServiceFactory.get_url(service), data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        reread_service = DigitalOceanService.objects.get(pk=service.pk)
        self.assertEqual(reread_service.customer, service.customer)

    def test_user_can_change_service_name_of_service_he_owns(self):
        self.client.force_authenticate(user=self.users['customer_owner'])

        service = self.services['owned']

        payload = {'name': 'new name'}
        response = self.client.patch(factories.DigitalOceanServiceFactory.get_url(service), data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        reread_service = DigitalOceanService.objects.get(pk=service.pk)
        self.assertEqual(reread_service.name, 'new name')

    def test_user_cannot_modify_in_unstable_state(self):
        self.client.force_authenticate(user=self.users['customer_owner'])

        for state in SynchronizationStates.UNSTABLE_STATES:
            service = factories.DigitalOceanServiceFactory(state=state, customer=self.customers['owned'])
            url = factories.DigitalOceanServiceFactory.get_url(service)

            for method in ('PUT', 'PATCH', 'DELETE'):
                func = getattr(self.client, method.lower())
                response = func(url)
                self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def _get_valid_payload(self, resource):
        return {
            'name': resource.name,
            'customer': structure_factories.CustomerFactory.get_url(resource.customer),
            'auth_token': resource.auth_token,
        }
