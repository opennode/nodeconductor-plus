from rest_framework import serializers

from nodeconductor.core.serializers import AugmentedSerializerMixin, GenericRelatedField
from nodeconductor.structure import models as structure_models
from nodeconductor_plus.premium_support import models


class PlanSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = models.Plan
        fields = ('url', 'uuid', 'name', 'description', 'base_rate', 'hour_rate')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class ContractSerializer(serializers.HyperlinkedModelSerializer):
    state = serializers.ReadOnlyField(source='get_state_display')
    project_name = serializers.ReadOnlyField(source='project.name')
    plan_name = serializers.ReadOnlyField(source='plan.name')

    class Meta:
        model = models.Contract

        fields = ('url', 'uuid', 'state', 'project', 'project_name', 'plan', 'plan_name')
        read_only_fields = ('state',)

        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'premium-support-contract-detail'},
            'plan': {'lookup_field': 'uuid', 'view_name': 'premium-support-plan-detail'},
            'project': {'lookup_field': 'uuid'},
        }

    def validate_project(self, project):
        if models.Contract.objects.filter(project=project)\
                 .exclude(state=models.Contract.States.CANCELLED).exists():
            raise serializers.ValidationError('Contract for this project already exists')

        return project


class SupportCaseSerializer(AugmentedSerializerMixin, serializers.HyperlinkedModelSerializer):
    resource = GenericRelatedField(related_models=models.get_resource_models(), required=False)

    class Meta:
        model = models.SupportCase

        fields = ('url', 'uuid', 'contract', 'name', 'description', 'created', 'modified', 'resource')
        protected_fields = ('contract', 'resource')

        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'premium-support-case-detail'},
            'contract': {'lookup_field': 'uuid', 'view_name': 'premium-support-contract-detail'},
        }

    def validate_contract(self, contract):
        if contract.state != models.Contract.States.APPROVED:
            raise serializers.ValidationError('Contract is not approved')
        return contract


class WorklogSerializer(AugmentedSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Worklog

        fields = ('url', 'uuid', 'support_case', 'time_spent', 'description', 'created')
        read_only_fields = ('created', )
        protected_fields = ('support_case', )

        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'premium-support-worklog-detail'},
            'support_case': {'lookup_field': 'uuid', 'view_name': 'premium-support-case-detail'},
        }


class ReportSerializer(serializers.Serializer):
    date = serializers.DateField()
    hours = serializers.IntegerField()
    price = serializers.DecimalField(decimal_places=2, max_digits=10)
