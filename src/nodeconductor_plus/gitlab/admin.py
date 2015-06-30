
from django.contrib import admin

from nodeconductor.structure.admin import HiddenServiceAdmin

from .models import GitLabService, Group, Project


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'backend_id', 'state')
    list_filter = ('state',)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'backend_id', 'state')
    list_filter = ('state',)


admin.site.register(GitLabService, HiddenServiceAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Project, ProjectAdmin)
