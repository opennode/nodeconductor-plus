from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import Service, ServiceProjectLink, Group, Project


admin.site.register(Group, structure_admin.ResourceAdmin)
admin.site.register(Project, structure_admin.ResourceAdmin)
admin.site.register(Service, structure_admin.ServiceAdmin)
admin.site.register(ServiceProjectLink, structure_admin.ServiceProjectLinkAdmin)
