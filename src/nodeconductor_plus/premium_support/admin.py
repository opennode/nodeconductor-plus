from django.contrib import admin

from .models import Plan, Contract


class PlanAdmin(admin.ModelAdmin):
    ordering = ['base_rate']
    list_display = ['name', 'base_rate', 'hour_rate']


class ContractAdmin(admin.ModelAdmin):
    list_display = ['project', 'plan', 'state']


admin.site.register(Plan, PlanAdmin)
admin.site.register(Contract, ContractAdmin)
