from django.contrib.contenttypes.models import ContentType

from nodeconductor.cost_tracking import CostTrackingBackend
from nodeconductor.cost_tracking.models import DefaultPriceListItem

from . import models


class DigitalOceanCostTrackingBackend(CostTrackingBackend):

    @classmethod
    def get_default_price_list_items(cls):
        ct = ContentType.objects.get_for_model(models.Droplet)
        # XXX: hardcode a list of sizes with prices since it's available only via API
        sizes = {
            '1gb': 10.0,
            '2gb': 20.0,
            '4gb': 40.0,
            '8gb': 80.0,
            '16gb': 160.0,
            '32gb': 320.0,
            '48gb': 480.0,
            '64gb': 640.0,
            '512mb': 5.0,
        }

        # sizes
        for name, price in sizes.items():
            yield DefaultPriceListItem(
                resource_content_type=ct,
                item_type='flavor',
                key=name,
                value=price)

    @classmethod
    def get_monthly_cost_estimate(cls, resource):
        backend = resource.get_backend()
        return backend.get_monthly_cost_estimate(resource)
