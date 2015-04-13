from django.contrib import admin

from .models import PlanQuota, Plan


class PlanQuotaInline(admin.TabularInline):
    model = PlanQuota
    fields = ('name', 'value')
    extra = 2
    can_delete = True


class PlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name']
    inlines = [PlanQuotaInline]


admin.site.register(Plan, PlanAdmin)
