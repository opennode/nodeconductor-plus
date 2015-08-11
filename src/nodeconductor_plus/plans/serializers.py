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


class OrderSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Order
        fields = ('url', 'uuid', 'customer', 'customer_name', 'plan',  'plan_name', 'plan_price',
                  'state', 'user', 'username', 'approval_url', 'start_date')
        read_only_fields = ('customer_name', 'plan_name', 'plan_price',
                            'state', 'user', 'username', 'approval_url', 'start_date')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'customer': {'lookup_field': 'uuid'},
            'plan': {'lookup_field': 'uuid'},
            'user': {'lookup_field': 'uuid'},
        }

    def get_fields(self):
        fields = super(OrderSerializer, self).get_fields()
        fields['customer'].required = True
        fields['plan'].required = True
        return fields

    def create(self, validated_data):
        try:
            validated_data['user'] = self.context['request'].user
        except AttributeError:
            raise AttributeError('OrderSerializer have to be initialized with `request` in context')
        return super(OrderSerializer, self).create(validated_data)
