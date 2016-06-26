from django.contrib import admin
from django.utils.translation import ungettext

from nodeconductor.core.tasks import send_task
from .models import PlanQuota, Plan, Agreement


class PlanQuotaInline(admin.TabularInline):
    model = PlanQuota
    fields = ('name', 'value')
    extra = 2
    can_delete = True


class PlanAdmin(admin.ModelAdmin):
    fields = ['name', 'price', 'is_default']
    list_display = ['name', 'price', 'is_default']
    search_fields = ['name']
    inlines = [PlanQuotaInline]
    ordering = ['price']


class AgreementAdmin(admin.ModelAdmin):
    list_display = ['customer', 'plan', 'state', 'backend_id']
    actions = ['generate_invoices']
    readonly_fields = ['approval_url', 'backend_id', 'token']

    def generate_invoices(self, request, queryset):
        for agreement in queryset.iterator():
            send_task('plans', 'generate_agreement_invoices')(agreement.id)

        tasks_scheduled = queryset.count()
        message = ungettext(
            'One agreement scheduled for invoices generation.',
            '%(tasks_scheduled)d agreements scheduled for invoices generation.',
            tasks_scheduled
        )
        message = message % {
            'tasks_scheduled': tasks_scheduled,
        }

        self.message_user(request, message)

    generate_invoices.short_description = "Generate agreement invoices"


admin.site.register(Plan, PlanAdmin)
admin.site.register(Agreement, AgreementAdmin)
