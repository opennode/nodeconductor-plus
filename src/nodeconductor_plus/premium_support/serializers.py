from rest_framework import serializers

from nodeconductor.structure import models as structure_models
from nodeconductor_plus.premium_support import models


class PlanSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Plan
        fields = ('url', 'uuid', 'name', 'description', 'base_hours', 'hour_rate')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class ContractSerializer(serializers.HyperlinkedModelSerializer):
    state = serializers.ReadOnlyField(source='get_state_display')

    class Meta:
        model = models.Contract

        fields = ('url', 'uuid', 'user', 'state', 'project', 'plan')
        read_only_fields = ('state', 'user')

        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'premium-support-contract-detail'},
            'plan': {'lookup_field': 'uuid', 'view_name': 'premium-support-plan-detail'},
            'user': {'lookup_field': 'uuid'},
            'project': {'lookup_field': 'uuid'},
        }

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super(ContractSerializer, self).create(validated_data)

    def validate_project(self, project):
        if models.Contract.objects.filter(project=project)\
                 .exclude(state=models.Contract.States.CANCELLED).exists():
            raise serializers.ValidationError('Contract for this project already exists')

        return project


class SupportCaseSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.SupportCase

        fields = ('url', 'uuid', 'contract', 'name', 'description', 'created', 'modified')
        read_only_fields = ('created', 'modified')

        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'premium-support-case-detail'},
            'contract': {'lookup_field': 'uuid', 'view_name': 'premium-support-contract-detail'},
        }

    def validate_contract(self, contract):
        if contract.state != models.Contract.States.APPROVED:
            raise serializers.ValidationError('Contract is not approved')
        return contract
