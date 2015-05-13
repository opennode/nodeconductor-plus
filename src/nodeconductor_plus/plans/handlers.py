from . import settings, models


def create_customer_plan(sender, instance=None, created=False, **kwargs):
    if not created:
        return

    customer = instance
    default_plan, created = models.Plan.objects.get_or_create(
        name=settings.DEFAULT_PLAN['name'], price=settings.DEFAULT_PLAN['price'])
    if created:
        for quota_name, quota_value in settings.DEFAULT_PLAN['quotas']:
            models.PlanQuota.objects.get_or_create(name=quota_name, value=quota_value, plan=default_plan)

    default_plan.plan_customers.create(customer=customer)
