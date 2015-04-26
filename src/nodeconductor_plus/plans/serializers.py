from rest_framework import serializers

import models


class PlanSerializer(serializers.HyperlinkedModelSerializer):

    quotas = serializers.SerializerMethodField()

    class Meta:
        model = models.Plan
        fields = ('url', 'uuid', 'name', 'price', 'quotas')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }

    def get_quotas(self, obj):
        return obj.quotas.values('name', 'value')


class OrderSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Order
        fields = ('url', 'uuid', 'customer', 'plan', 'customer_name', 'plan_name', 'plan_price', 'state')
        read_only_fields = ('customer_name', 'plan_name', 'plan_price', 'state')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'customer': {'lookup_field': 'uuid'},
            'plan': {'lookup_field': 'uuid'},
        }
