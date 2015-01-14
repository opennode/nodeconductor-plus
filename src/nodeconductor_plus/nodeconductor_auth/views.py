import json
import os
import random
import requests
import string
from urlparse import parse_qsl
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import views, status, response
from rest_framework.authtoken.models import Token

from .models import AuthProfile


nc_plus_settings = getattr(settings, 'NODECONDUCTOR_PLUS', {})
GOOGLE_SECRET = nc_plus_settings['GOOGLE_SECRET']
FACEBOOK_SECRET = nc_plus_settings['FACEBOOK_SECRET']


def generate_password(length=10):
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))

    return ''.join(random.choice(chars) for i in range(length))


def generate_username(name):
    return name + ' ' + uuid.uuid4().hex


class GoogleView(views.APIView):

    permission_classes = []
    authentication_classes = []

    def post(self, request, format=None):
        access_token_url = 'https://accounts.google.com/o/oauth2/token'
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
        profile = json.loads(r.text)

        # Step 3. Create a new user or get existing one.
        try:
            profile = AuthProfile.objects.get(google=profile['sub'])
            token, _ = Token.objects.get_or_create(user=profile.user)
            return response.Response({'token': token.key}, status=status.HTTP_200_OK)
        except AuthProfile.DoesNotExist:
            user = get_user_model().objects.create_user(
                username=generate_username(profile['name']), password=generate_password())
            user.auth_profile.google = profile['sub']
            user.auth_profile.save()
            token, _ = Token.objects.get_or_create(user=user)
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
        access_token = dict(parse_qsl(r.text))

        # Step 2. Retrieve information about the current user.
        r = requests.get(graph_api_url, params=access_token)
        profile = json.loads(r.text)

        # Step 3. Create a new user or get existing one.
        try:
            profile = AuthProfile.objects.get(facebook=profile['id'])
            token, _ = Token.objects.get_or_create(user=profile.user)
            return response.Response({'token': token.key}, status=status.HTTP_200_OK)
        except AuthProfile.DoesNotExist:
            user = get_user_model().objects.create_user(
                username=generate_username(profile['name']), password=generate_password())
            user.auth_profile.facebook = profile['id']
            user.auth_profile.save()
            token, _ = Token.objects.get_or_create(user=user)
            return response.Response({'token': token.key}, status=status.HTTP_201_CREATED)
