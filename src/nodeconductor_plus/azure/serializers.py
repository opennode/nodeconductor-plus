from rest_framework import serializers

from django.utils import dateparse

from nodeconductor.structure import SupportedServices
from nodeconductor.structure import serializers as structure_serializers

from . import models
from .backend import AzureBackendError


class ImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta(object):
        model = models.Image
        view_name = 'azure-image-detail'
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class LocationSerializer(serializers.HyperlinkedModelSerializer):

    class Meta(object):
        model = models.Location
        view_name = 'azure-location-detail'
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_TYPE = SupportedServices.Types.Azure
    SERVICE_ACCOUNT_FIELDS = {
        'username': 'Subscription id in the form of GUID',
        'token': 'Access token',
    }

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.AzureService
        view_name = 'azure-detail'


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):

    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.AzureServiceProjectLink
        view_name = 'azure-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'azure-detail'},
        }


class VirtualMachineSerializer(structure_serializers.VirtualMachineSerializer):

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='azure-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='azure-spl-detail',
        queryset=models.AzureServiceProjectLink.objects.all(),
        write_only=True)

    image = serializers.HyperlinkedRelatedField(
        view_name='azure-image-detail',
        lookup_field='uuid',
        queryset=models.Image.objects.all().select_related('settings'),
        write_only=True)

    class Meta(structure_serializers.VirtualMachineSerializer.Meta):
        model = models.VirtualMachine
        view_name = 'azure-virtualmachine-detail'
        fields = structure_serializers.VirtualMachineSerializer.Meta.fields + (
            'image',
        )
        protected_fields = structure_serializers.VirtualMachineSerializer.Meta.protected_fields + (
            'image',
        )

    def validate(self, attrs):
        raise NotImplementedError


class VirtualMachineImportSerializer(structure_serializers.BaseResourceImportSerializer):

    class Meta(structure_serializers.BaseResourceImportSerializer.Meta):
        model = models.VirtualMachine
        view_name = 'azure-virtualmachine-detail'

    def create(self, validated_data):
        backend = self.context['service'].get_backend()
        try:
            vm = backend.get_vm(validated_data['backend_id'])
        except AzureBackendError:
            raise serializers.ValidationError(
                {'backend_id': "Can't find Virtual Machine with ID %s" % validated_data['backend_id']})

        validated_data['name'] = vm.service_name
        validated_data['description'] = vm.hosted_service_properties.description
        validated_data['created'] = dateparse.parse_datetime(vm.hosted_service_properties.date_created)
        validated_data['state'] = models.VirtualMachine.States.ONLINE

        return super(VirtualMachineImportSerializer, self).create(validated_data)
