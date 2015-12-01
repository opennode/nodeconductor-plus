from django.contrib import admin
from django.utils.translation import ungettext

from nodeconductor.core.tasks import send_task
from nodeconductor_paypal.backend import PayPalError
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
            except PayPalError:
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
    actions = ['sync_invoices']

    def sync_invoices(self, request, queryset):
        tasks_scheduled = 0

        for agreement in queryset.iterator():
            send_task('plans', 'sync_invoices')(agreement.id)
            tasks_scheduled += 1

        message = ungettext(
            'One agreement scheduled for invoices sync.',
            '%(tasks_scheduled)d agreements scheduled for invoices sync.',
            tasks_scheduled
        )
        message = message % {
            'tasks_scheduled': tasks_scheduled,
        }

        self.message_user(request, message)

    sync_invoices.short_description = "Sync agreement invoices"


admin.site.register(Plan, PlanAdmin)
admin.site.register(Agreement, AgreementAdmin)
