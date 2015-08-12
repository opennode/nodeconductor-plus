from . import settings, models


def create_customer_plan(sender, instance=None, created=False, **kwargs):
    if not created:
        return

    apply_default_plan(instance)


def apply_default_plan(customer):
    default_plan, created = models.Plan.objects.get_or_create(
        name=settings.DEFAULT_PLAN['name'], price=settings.DEFAULT_PLAN['price'])
    if created:
        for quota_name, quota_value in settings.DEFAULT_PLAN['quotas']:
            models.PlanQuota.objects.get_or_create(name=quota_name, value=quota_value, plan=default_plan)

    agreement = models.Agreement.objects.create(plan=default_plan,
                                                customer=customer,
                                                state=models.Agreement.States.ACTIVE)
    agreement.apply_quotas()
