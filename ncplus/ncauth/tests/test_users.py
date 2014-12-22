from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from rest_framework import test, status


class SignupTest(test.APITransactionTestCase):

    def setUp(self):
        self.url = reverse('ncauth_signup')

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


class SigninTest(test.APITransactionTestCase):

    def setUp(self):
        self.url = reverse('ncauth_signin')
        self.data = {
            'username': 'test_username',
            'password': 'test_password',
        }

    def test_user_can_signin(self):
        user = get_user_model().objects.create_user(**self.data)
        # when
        response = self.client.post(self.url, self.data)
        # then
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], user.id)

    def test_user_can_not_signin_if_he_does_not_exist(self):
        # when
        response = self.client.post(self.url, self.data)
        # then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_can_not_signin_if_he_is_not_active(self):
        user = get_user_model().objects.create_user(**self.data)
        user.is_active = False
        user.save()
        # when
        response = self.client.post(self.url, self.data)
        # then
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
