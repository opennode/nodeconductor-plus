from nodeconductor.cost_tracking import CostTrackingRegister, CostTrackingStrategy, ConsumableItem

from . import models


class DropletStrategy(CostTrackingStrategy):
    resource_class = models.Droplet

    class Types(object):
        FLAVOR = 'flavor'

    @classmethod
    def get_consumable_items(cls):
        return [ConsumableItem(item_type=cls.Types.FLAVOR, key=size.name, default_price=size.price)
                for size in models.Size.objects.all()]

    @classmethod
    def get_configuration(cls, instance):
        return {}


CostTrackingRegister.register_strategy(DropletStrategy)
