from nodeconductor_plus.plans.models import Agreement


def create_customer_plan(sender, instance=None, created=False, **kwargs):
    if not created:
        return

    Agreement.apply_default_plan(instance)
