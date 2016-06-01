from django.contrib.contenttypes.models import ContentType
from libcloud.compute.drivers.ec2 import INSTANCE_TYPES

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem

from . import models


class AWSCostTrackingBackend(CostTrackingBackend):

    @classmethod
    def get_default_price_list_items(cls):
        ct = ContentType.objects.get_for_model(models.Instance)
        for size in models.Size.objects.iterator():
            yield DefaultPriceListItem(
                resource_content_type=ct,
                item_type=CostTrackingBackend.VM_SIZE_ITEM_TYPE,
                key=size.backend_id,
                value=size.price,
                metadata={
                    'name': INSTANCE_TYPES[size.backend_id]['name'],
                    'disk': size.disk,
                    'ram': size.ram,
                    'cores': size.cores,
                })

    @classmethod
    def get_monthly_cost_estimate(cls, resource):
        backend = resource.get_backend()
        return backend.get_monthly_cost_estimate(resource)
