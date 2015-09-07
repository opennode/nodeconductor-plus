from django.contrib import admin

from nodeconductor.billing.backend import BillingBackendError
from .models import PlanQuota, Plan, Agreement


class PlanQuotaInline(admin.TabularInline):
    model = PlanQuota
    fields = ('name', 'value')
    extra = 2
    can_delete = True


class PlanAdmin(admin.ModelAdmin):
    fields = ['name', 'price']
    list_display = ['name', 'price', 'backend_id']
    search_fields = ['name']
    inlines = [PlanQuotaInline]
    actions = ['push_to_backend']
    ordering = ['price']

    def push_to_backend(self, request, queryset):
        erred_plans = []
        for plan in queryset:
            try:
                plan.push_to_backend(request)
            except BillingBackendError:
                erred_plans.append(plan)
        if not erred_plans:
            message = 'All billing plans have been pushed to backend successfully'
        else:
            names = ', '.join([plan.name for plan in erred_plans])
            message = 'Failed to push billing plans: %s' % names
        self.message_user(request, message)

    push_to_backend.short_description = 'Push billing plans to backend'


class AgreementAdmin(admin.ModelAdmin):
    list_display = ['customer', 'plan', 'state']


admin.site.register(Plan, PlanAdmin)
admin.site.register(Agreement, AgreementAdmin)
