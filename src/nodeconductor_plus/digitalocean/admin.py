
from django.contrib import admin

from nodeconductor.structure.admin import HiddenServiceAdmin

from .models import Service, Droplet


class DropletAdmin(admin.ModelAdmin):
    list_display = ('name', 'backend_id', 'state')
    list_filter = ('state',)


admin.site.register(Service, HiddenServiceAdmin)
admin.site.register(Droplet, DropletAdmin)
