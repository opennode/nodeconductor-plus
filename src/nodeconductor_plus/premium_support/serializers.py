from rest_framework import serializers

from nodeconductor.core.serializers import AugmentedSerializerMixin, GenericRelatedField
from nodeconductor.core.signals import pre_serializer_fields
from nodeconductor.structure import models as structure_models
from nodeconductor.structure.serializers import ProjectSerializer
from nodeconductor_plus.premium_support import models


def get_plan_for_project(serializer, project):
    if 'plans' not in serializer.context:
        contracts = models.Contract.objects\
            .filter(state=models.Contract.States.APPROVED).select_related('plan')
        if isinstance(serializer.instance, list):
            contracts = contracts.filter(project__in=serializer.instance)
        else:
            contracts = contracts.filter(project=serializer.instance)
        serializer.context['plans'] = {
            contract.project_id: contract.plan for contract in list(contracts)
        }
    plan = serializer.context['plans'].get(project.id)
    if plan:
        serializer = BasicPlanSerializer(instance=plan, context=serializer.context)
        return serializer.data


def get_pending_contracts_for_project(serializer, project):
    if 'has_pending_contracts' not in serializer.context:
        contracts = models.Contract.objects.filter(state=models.Contract.States.REQUESTED)
        serializer.context['has_pending_contracts'] = set(
            contract.project_id for contract in contracts
        )
    return project.id in serializer.context['has_pending_contracts']


def add_plan_for_project(sender, fields, **kwargs):
    fields['plan'] = serializers.SerializerMethodField()
    setattr(sender, 'get_plan', get_plan_for_project)


pre_serializer_fields.connect(
    add_plan_for_project,
    sender=ProjectSerializer
)


def add_has_pending_contracts(sender, fields, **kwargs):
    fields['has_pending_contracts'] = serializers.SerializerMethodField()
    setattr(sender, 'get_has_pending_contracts', get_plan_for_project)


pre_serializer_fields.connect(
    add_has_pending_contracts,
    sender=ProjectSerializer
)


class BasicPlanSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Plan
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'premium-support-plan-detail'}
        }


class PlanSerializer(BasicPlanSerializer):
    class Meta(BasicPlanSerializer.Meta):
        fields = BasicPlanSerializer.Meta.fields + ('description',  'terms', 'base_rate', 'hour_rate')


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
        if models.Contract.objects.filter(
                project=project, state=models.Contract.States.APPROVED).exists():
            raise serializers.ValidationError('Contract for this project already exists')

        return project

    def get_customer(self):
        return self.validated_data['project'].customer


class SupportCaseSerializer(AugmentedSerializerMixin, serializers.HyperlinkedModelSerializer):
    resource = GenericRelatedField(related_models=structure_models.Resource.get_all_models(), required=False)

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

    def get_customer(self):
        return self.validated_data['contract'].project.customer


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
