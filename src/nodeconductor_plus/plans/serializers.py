from rest_framework import serializers

from . import models


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


class PlanCustomerSerializer(serializers.HyperlinkedModelSerializer):

    plan = PlanSerializer()

    class Meta:
        model = models.PlanCustomer
        fields = ('url', 'uuid', 'customer', 'plan')
        view_name = 'plan_customer-detail'
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'customer': {'lookup_field': 'uuid'},
        }
