from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import AWSService, AWSServiceProjectLink, Instance, Image, Region


class ImageAdmin(admin.ModelAdmin):
    fields = 'name', 'region', 'backend_id'
    list_display = 'name', 'region', 'backend_id'
    list_filter = 'region',


class ImageInline(admin.TabularInline):
    model = Image
    extra = 1


class RegionAdmin(structure_admin.ProtectedModelMixin, admin.ModelAdmin):
    readonly_fields = 'name', 'backend_id'
    inlines = ImageInline,


admin.site.register(Image, ImageAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Instance, structure_admin.VirtualMachineAdmin)
admin.site.register(AWSService, structure_admin.ServiceAdmin)
admin.site.register(AWSServiceProjectLink, structure_admin.ServiceProjectLinkAdmin)
