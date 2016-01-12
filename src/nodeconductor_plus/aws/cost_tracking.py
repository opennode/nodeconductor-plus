from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem

from .backend import EC2NodeDriver
from . import models


class AWSCostTrackingBackend(CostTrackingBackend):

    @classmethod
    def get_default_price_list_items(cls):
        ct = ContentType.objects.get_for_model(models.Instance)
        for size in EC2NodeDriver(None, None).list_sizes():
            yield DefaultPriceListItem(
                resource_content_type=ct,
                item_type=CostTrackingBackend.VM_SIZE_ITEM_TYPE,
                key=size.id,
                value=size.price)

    @classmethod
    def get_monthly_cost_estimate(cls, resource):
        backend = resource.get_backend()
        return backend.get_monthly_cost_estimate(resource)
