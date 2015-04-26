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
        fields = ('url', 'uuid', 'customer', 'plan', 'customer_name', 'plan_name', 'plan_price', 'state', 'user')
        read_only_fields = ('customer_name', 'plan_name', 'plan_price', 'state', 'user')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'customer': {'lookup_field': 'uuid'},
            'plan': {'lookup_field': 'uuid'},
            'user': {'lookup_field': 'uuid'},
        }

    def create(self, validated_data):
        try:
            validated_data['user'] = self.context['request'].user
        except AttributeError:
            raise AttributeError('OrderSerializer have to be initialized with `request` in context')
        return super(OrderSerializer, self).create(validated_data)
