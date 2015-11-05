from django.contrib import admin
from django.utils.translation import ungettext

from .models import Plan, Contract


class PlanAdmin(admin.ModelAdmin):
    ordering = ['base_rate']
    list_display = ['name', 'base_rate', 'hour_rate']


class ContractAdmin(admin.ModelAdmin):
    list_display = ['project', 'plan', 'state']

    actions = [
        'approve',
    ]

    def approve(self, request, queryset):
        count = 0
        for contract in queryset:
            if contract.state == Contract.States.REQUESTED:
                contract.approve()
                contract.save()
                count += 1

        message = ungettext(
            'One premium support contract has been approved',
            '%(count)d premium support contract have been approved',
            count
        )
        message = message % {'count': count}

        self.message_user(request, message)

    approve.short_description = "Approve selected contracts"


admin.site.register(Plan, PlanAdmin)
admin.site.register(Contract, ContractAdmin)
