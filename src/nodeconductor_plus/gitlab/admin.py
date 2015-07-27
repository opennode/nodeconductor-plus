from django.contrib import admin

from nodeconductor.structure import admin as structure_admin
from .models import GitLabService, GitLabServiceProjectLink, Group, Project


admin.site.register(Group, structure_admin.ResourceAdmin)
admin.site.register(Project, structure_admin.ResourceAdmin)
admin.site.register(GitLabService, structure_admin.ServiceAdmin)
admin.site.register(GitLabServiceProjectLink, structure_admin.ServiceProjectLinkAdmin)
