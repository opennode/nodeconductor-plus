from nodeconductor_plus.insights.tasks import check_service_resources


def check_unmanaged_resources(sender, instance, created=False, **kwargs):
    if created:
        check_service_resources.delay(instance.to_string())
