from django.db import models
from django.conf import settings


class AuthProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='auth_profile')
    google = models.CharField(max_length=120, blank=True, unique=True)
    facebook = models.CharField(max_length=120, blank=True, unique=True)
