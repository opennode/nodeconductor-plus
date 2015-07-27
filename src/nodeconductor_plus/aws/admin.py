from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import Service, ServiceProjectLink, Instance


admin.site.register(Instance, structure_admin.ResourceAdmin)
admin.site.register(Service, structure_admin.ServiceAdmin)
admin.site.register(ServiceProjectLink, structure_admin.ServiceProjectLinkAdmin)
