import mock

from rest_framework import status, test
from rest_framework.reverse import reverse

from nodeconductor.structure.tests import factories as structure_factories

from ..models import AuthProfile


class AuthTest(test.APITransactionTestCase):
    def setUp(self):
        self.valid_data = {
            'clientId': '4242324',
            'redirectUri': 'http://example.com/redirect/',
            'code': 'secret'
        }

    def test_auth_view_works_for_anonymous_only(self):
        user = structure_factories.UserFactory()
        self.client.force_authenticate(user)
        response = self.client.post(reverse('auth_google'), self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_input_data_is_validated(self):
        response = self.client.post(reverse('auth_google'), {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_if_google_auth_succeeded_user_and_profile_is_created(self):
        with mock.patch('nodeconductor_plus.nodeconductor_auth.'
                        'views.GoogleView.get_backend_user') as get_backend_user:
            get_backend_user.return_value = {
                'id': '123',
                'name': 'Google user'
            }
            response = self.client.post(reverse('auth_google'), self.valid_data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
            self.assertEqual('Google user', AuthProfile.objects.get(google='123').user.full_name)

    def test_if_user_already_exists_it_is_not_created_again(self):
        user = structure_factories.UserFactory()
        user.auth_profile.google = '123'
        user.auth_profile.save()

        with mock.patch('nodeconductor_plus.nodeconductor_auth.'
                        'views.GoogleView.get_backend_user') as get_backend_user:
            get_backend_user.return_value = {
                'id': '123',
                'name': 'Google user'
            }
            response = self.client.post(reverse('auth_google'), self.valid_data)
            self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_if_facebook_auth_succeeded_user_and_profile_is_created(self):
        with mock.patch('nodeconductor_plus.nodeconductor_auth.'
                        'views.FacebookView.get_backend_user') as get_backend_user:
            get_backend_user.return_value = {
                'id': '123',
                'name': 'Facebook user'
            }
            response = self.client.post(reverse('auth_facebook'), self.valid_data)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
            self.assertEqual('Facebook user', AuthProfile.objects.get(facebook='123').user.full_name)
