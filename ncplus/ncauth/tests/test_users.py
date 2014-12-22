from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from rest_framework import test, status


class SignupTest(test.APITransactionTestCase):

    def setUp(self):
        self.url = reverse('auth_signup')

    def test_user_can_be_signed_up(self):
        data = {
            'username': 'test_username',
            'password': 'test_password',
        }
        # when
        response = self.client.post(self.url, data)
        # then
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            get_user_model().objects.filter(username=data['username']).exists(), 'Created user have to exist in db')

    def test_user_with_dublicated_username_can_not_be_created(self):
        data = {
            'username': 'test_username',
            'password': 'test_password',
        }
        get_user_model().objects.create_user(**data)
        # when
        response = self.client.post(self.url, data)
        # then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


