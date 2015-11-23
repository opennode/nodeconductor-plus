import json
import os
import random
import requests
import string
from urlparse import parse_qsl
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import views, status, response, generics
from rest_framework.authtoken.models import Token

from nodeconductor.core.tasks import send_task
from .models import AuthProfile
from .serializers import RegistrationSerializer, ActivationSerializer


nc_plus_settings = getattr(settings, 'NODECONDUCTOR_PLUS', {})
GOOGLE_SECRET = nc_plus_settings.get('GOOGLE_SECRET')
FACEBOOK_SECRET = nc_plus_settings.get('FACEBOOK_SECRET')


class AuthException(Exception):
    pass


class FacebookException(AuthException):
    def __init__(self, facebook_error):
        self.message_text = facebook_error.get('message', 'Undefined')
        self.message_type = facebook_error.get('type', 'Undefined')
        self.message_code = facebook_error.get('code', 'Undefined')
        self.message = 'Facebook error {} (code:{}): {}'.format(self.message_type, self.message_code, self.message_text)

    def __str__(self):
        return self.message


class GoogleException(AuthException):
    def __init__(self, google_error):
        self.message_text = google_error.get('message', 'Undefined')
        self.message_code = google_error.get('code', 'Undefined')
        self.message = 'Google error (code:{}): {}'.format(self.message_code, self.message_text)

    def __str__(self):
        return self.message


def generate_password(length=10):
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))

    return ''.join(random.choice(chars) for i in range(length))


def generate_username(name):
    return uuid.uuid4().hex[:30]


class GoogleView(views.APIView):

    permission_classes = []
    authentication_classes = []

    def post(self, request, format=None):
        access_token_url = 'https://www.googleapis.com/oauth2/v3/token'
        people_api_url = 'https://www.googleapis.com/plus/v1/people/me/openIdConnect'

        payload = dict(client_id=request.DATA['clientId'],
                       redirect_uri=request.DATA['redirectUri'],
                       client_secret=GOOGLE_SECRET,
                       code=request.DATA['code'],
                       grant_type='authorization_code')

        # Step 1. Exchange authorization code for access token.
        r = requests.post(access_token_url, data=payload)

        token = json.loads(r.text)
        headers = {'Authorization': 'Bearer {0}'.format(token['access_token'])}

        # Step 2. Retrieve information about the current user.
        r = requests.get(people_api_url, headers=headers)
        response_data = json.loads(r.text)

        # Step 3. Check is response valid.
        if 'error' in response_data:
            raise GoogleException(response_data['error'])

        # Step 4. Create a new user or get existing one.
        try:
            profile = AuthProfile.objects.get(google=response_data['sub'])
            token = Token.objects.get(user=profile.user)
            if profile.user.full_name != response_data['name']:
                profile.user.full_name = response_data['name']
                profile.user.save()
            return response.Response({'token': token.key}, status=status.HTTP_200_OK)
        except AuthProfile.DoesNotExist:
            user = get_user_model().objects.create_user(
                username=generate_username(response_data['name']),
                password=generate_password(),
                full_name=response_data['name'],
            )
            user.auth_profile.google = response_data['sub']
            user.auth_profile.save()
            token = Token.objects.get(user=user)
            return response.Response({'token': token.key}, status=status.HTTP_201_CREATED)


class FacebookView(views.APIView):

    permission_classes = []
    authentication_classes = []

    def post(self, request, format=None):
        access_token_url = 'https://graph.facebook.com/oauth/access_token'
        graph_api_url = 'https://graph.facebook.com/me'

        params = {
            'client_id': request.DATA['clientId'],
            'redirect_uri': request.DATA['redirectUri'],
            'client_secret': FACEBOOK_SECRET,
            'code': request.DATA['code']
        }

        # Step 1. Exchange authorization code for access token.
        r = requests.get(access_token_url, params=params)
        self.check_response(r)
        access_token = dict(parse_qsl(r.text))

        # Step 2. Retrieve information about the current user.
        r = requests.get(graph_api_url, params=access_token)
        self.check_response(r)
        response_data = r.json()

        # Step 3. Create a new user or get existing one.
        try:
            profile = AuthProfile.objects.get(facebook=response_data['id'])
            token = Token.objects.get(user=profile.user)
            if profile.user.full_name != response_data['name']:
                profile.user.full_name = response_data['name']
                profile.user.save()
            return response.Response({'token': token.key}, status=status.HTTP_200_OK)
        except AuthProfile.DoesNotExist:
            user = get_user_model().objects.create_user(
                username=generate_username(response_data['name']),
                password=generate_password(),
                full_name=response_data['name']
            )
            user.auth_profile.facebook = response_data['id']
            user.auth_profile.save()
            token = Token.objects.get(user=user)
            return response.Response({'token': token.key}, status=status.HTTP_201_CREATED)

    def check_response(self, r, valid_response=requests.codes.ok):
        if r.status_code != valid_response:
            try:
                data = r.json()
                error_message = data['error']
            except:
                values = (r.reason, r.status_code)
                error_message = 'Message: %s, status code: %s' % values
            raise FacebookException(error_message)


class RegistrationView(generics.CreateAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = RegistrationSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_active = False
        user.save()
        send_task('nodeconductor_auth', 'send_activation_email')(user.uuid.hex)


class ActivationView(views.APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        serializer = ActivationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.user.is_active = True
        serializer.user.save()

        token = Token.objects.get(user=serializer.user)
        return response.Response({'token': token.key}, status=status.HTTP_201_CREATED)
