from django.db import models
from django.conf import settings


class AuthProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='auth_profile')
