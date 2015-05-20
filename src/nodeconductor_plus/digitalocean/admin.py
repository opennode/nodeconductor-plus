
from django.contrib import admin

from nodeconductor.structure.admin import HiddenServiceAdmin

from .models import DigitalOceanService


admin.site.register(DigitalOceanService, HiddenServiceAdmin)
