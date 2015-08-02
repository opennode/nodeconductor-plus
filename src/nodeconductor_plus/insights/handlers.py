from nodeconductor_plus.insights.utils import check_service


def check_unmanaged_resources(sender, instance, created, **kwargs):
    if created:
        check_service(instance)
