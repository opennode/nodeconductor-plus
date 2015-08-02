from celery import shared_task

from nodeconductor.structure.models import Service
from nodeconductor_plus.insights.utils import check_service


@shared_task(name='nodeconductor.insights.check_unmanaged_resources')
def check_unmanaged_resources():
    for model in Service.get_all_models():
        for service in model.objects.all():
            check_service(service)
