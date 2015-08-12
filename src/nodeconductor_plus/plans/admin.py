from django.contrib import admin

from .models import PlanQuota, Plan


class PlanQuotaInline(admin.TabularInline):
    model = PlanQuota
    fields = ('name', 'value')
    extra = 2
    can_delete = True


class PlanAdmin(admin.ModelAdmin):
    fields = ['name', 'price']
    list_display = ['name', 'price']
    search_fields = ['name']
    inlines = [PlanQuotaInline]
    actions = ['push_to_backend']

    def push_to_backend(self, request, queryset):
        for plan in queryset:
            plan.push_to_backend(request)


admin.site.register(Plan, PlanAdmin)
