from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import AWSService, AWSServiceProjectLink, Instance


admin.site.register(Instance, structure_admin.ResourceAdmin)
admin.site.register(AWSService, structure_admin.ServiceAdmin)
admin.site.register(AWSServiceProjectLink, structure_admin.ServiceProjectLinkAdmin)
