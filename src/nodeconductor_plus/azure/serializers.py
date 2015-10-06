import re

from django.utils import six, timezone
from rest_framework import serializers
from rest_framework.reverse import reverse

from nodeconductor.structure import SupportedServices
from nodeconductor.structure import serializers as structure_serializers

from . import models
from .backend import AzureBackendError, SizeQueryset


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_TYPE = SupportedServices.Types.Azure
    SERVICE_ACCOUNT_FIELDS = {
        'username': 'In the format of GUID',
        'certificate': '',
    }
    SERVICE_ACCOUNT_EXTRA_FIELDS = {
        'location': '',
    }

    location = serializers.ChoiceField(
        choices=models.AzureService.Locations,
        write_only=True,
        required=False,
        allow_blank=True)

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.AzureService
        view_name = 'azure-detail'

    def get_fields(self):
        fields = super(ServiceSerializer, self).get_fields()
        fields['username'].label = 'Subscription ID'
        fields['certificate'].label = 'Private certificate file'
        return fields


class ImageSerializer(structure_serializers.BasePropertySerializer):

    SERVICE_TYPE = SupportedServices.Types.Azure

    class Meta(object):
        model = models.Image
        view_name = 'azure-image-detail'
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class SizeSerializer(six.with_metaclass(structure_serializers.PropertySerializerMetaclass,
                                        serializers.Serializer)):

    SERVICE_TYPE = SupportedServices.Types.Azure

    uuid = serializers.ReadOnlyField()
    url = serializers.SerializerMethodField()
    name = serializers.ReadOnlyField()
    cores = serializers.ReadOnlyField()
    ram = serializers.ReadOnlyField()
    disk = serializers.ReadOnlyField()

    class Meta(object):
        model = models.Size

    def get_url(self, size):
        return reverse('azure-size-detail', kwargs={'uuid': size.uuid}, request=self.context.get('request'))


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):

    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.AzureServiceProjectLink
        view_name = 'azure-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'azure-detail'},
        }


class VirtualMachineSerializer(structure_serializers.BaseResourceSerializer):

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

    size = serializers.HyperlinkedRelatedField(
        view_name='azure-size-detail',
        lookup_field='uuid',
        queryset=SizeQueryset(),
        write_only=True)

    username = serializers.CharField(write_only=True, required=True)
    # XXX: it's rather insecure
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})

    rdp = serializers.HyperlinkedIdentityField(view_name='azure-virtualmachine-rdp', lookup_field='uuid')

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.VirtualMachine
        view_name = 'azure-virtualmachine-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'image', 'size', 'username', 'password', 'user_data', 'rdp'
        )
        protected_fields = structure_serializers.BaseResourceSerializer.Meta.protected_fields + (
            'image', 'size', 'username', 'password', 'user_data'
        )

    def validate(self, attrs):
        if not re.match(r'[a-zA-Z0-9-]+', attrs['name']):
            raise serializers.ValidationError(
                "Only valid hostname characters are allowed. (a-z, A-Z, 0-9 and -)")

        # passwords must contain characters from at least three of the following four categories:
        groups = (r'[a-z]', r'[A-Z]', r'[0-9]', r'[^a-zA-Z\d\s:]')
        if not 6 <= len(attrs['password']) <= 72 or sum(bool(re.search(g, attrs['password'])) for g in groups) < 3:
            raise serializers.ValidationError(
                "The supplied password must be 6-72 characters long "
                "and meet password complexity requirements")

        return attrs


class VirtualMachineImportSerializer(structure_serializers.BaseResourceImportSerializer):

    class Meta(structure_serializers.BaseResourceImportSerializer.Meta):
        model = models.VirtualMachine
        view_name = 'azure-virtualmachine-detail'
        fields = structure_serializers.BaseResourceImportSerializer.Meta.fields + (
            'cores', 'ram', 'disk',
            'external_ips', 'internal_ips',
        )

    def create(self, validated_data):
        spl = validated_data['service_project_link']
        backend = spl.get_backend()

        try:
            vm = backend.get_vm(validated_data['backend_id'])
        except AzureBackendError:
            raise serializers.ValidationError(
                {'backend_id': "Can't find Virtual Machine with ID %s" % validated_data['backend_id']})

        validated_data['name'] = vm.name
        validated_data['created'] = timezone.now()
        validated_data['ram'] = vm.size.ram
        validated_data['disk'] = vm.size.disk
        validated_data['cores'] = vm.size.extra['cores']
        validated_data['external_ips'] = vm.public_ips[0]
        validated_data['internal_ips'] = vm.private_ips[0]
        validated_data['state'] = models.VirtualMachine.States.ONLINE \
            if vm.extra['power_state'] == 'Started' else models.VirtualMachine.States.OFFLINE

        return super(VirtualMachineImportSerializer, self).create(validated_data)
