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


class AgreementSerializer(serializers.HyperlinkedModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.name')
    plan_name = serializers.ReadOnlyField(source='plan.name')
    plan_price = serializers.ReadOnlyField(source='plan.price')
    user_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = models.Agreement
        fields = ('url', 'uuid', 'state', 'created', 'modified', 'approval_url',
                  'user', 'user_name', 'customer', 'customer_name', 'plan', 'plan_name', 'plan_price')
        read_only_fields = ('state', 'user', 'approval_url')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'customer': {'lookup_field': 'uuid'},
            'plan': {'lookup_field': 'uuid'},
            'user': {'lookup_field': 'uuid'},
        }

    def get_fields(self):
        fields = super(AgreementSerializer, self).get_fields()
        fields['customer'].required = True
        fields['plan'].required = True
        return fields

    def create(self, validated_data):
        try:
            validated_data['user'] = self.context['request'].user
        except AttributeError:
            raise AttributeError('AgreementSerializer have to be initialized with `request` in context')
        return super(AgreementSerializer, self).create(validated_data)
