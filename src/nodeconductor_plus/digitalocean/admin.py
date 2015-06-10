
from django.contrib import admin

from nodeconductor.structure.admin import HiddenServiceAdmin

from .models import DigitalOceanService, Droplet


class DropletAdmin(admin.ModelAdmin):
    list_display = ('name', 'backend_id', 'state')
    list_filter = ('state',)


admin.site.register(DigitalOceanService, HiddenServiceAdmin)
admin.site.register(Droplet, DropletAdmin)
