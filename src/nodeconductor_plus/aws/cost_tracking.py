from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem

from .backend import EC2NodeDriver
from . import models


class AWSCostTrackingBackend(CostTrackingBackend):

    @classmethod
    def get_default_price_list_items(cls):
        ct = ContentType.objects.get_for_model(models.Instance)
        sizes = {s.id: s.price for s in EC2NodeDriver(None, None).list_sizes()}

        # instances
        for name, price in sizes.items():
            yield DefaultPriceListItem(
                resource_content_type=ct,
                item_type='instance',
                key=name,
                value=price)

    @classmethod
    def get_monthly_cost_estimate(cls, resource):
        backend = resource.get_backend()
        return backend.get_monthly_cost_estimate(resource)
