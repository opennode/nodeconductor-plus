from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import AWSService, AWSServiceProjectLink, Instance, Image


class ImageAdmin(admin.ModelAdmin):
    fields = 'name', 'region', 'backend_id'
    list_display = 'name', 'region', 'backend_id'
    list_filter = 'region',


admin.site.register(Image, ImageAdmin)
admin.site.register(Instance, structure_admin.VirtualMachineAdmin)
admin.site.register(AWSService, structure_admin.ServiceAdmin)
admin.site.register(AWSServiceProjectLink, structure_admin.ServiceProjectLinkAdmin)
