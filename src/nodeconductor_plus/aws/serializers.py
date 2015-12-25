from django.utils import six
from rest_framework import serializers
from rest_framework.reverse import reverse

from nodeconductor.structure import serializers as structure_serializers

from . import models
from .backend import AWSBackendError, SizeQueryset


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_ACCOUNT_FIELDS = {
        'username': '',
        'token': '',
    }
    SERVICE_ACCOUNT_EXTRA_FIELDS = {
        'region': '',
    }

    region = serializers.ChoiceField(choices=models.AWSService.Regions,
                                     write_only=True,
                                     required=False,
                                     allow_blank=True)

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.AWSService
        view_name = 'aws-detail'

    def get_fields(self):
        fields = super(ServiceSerializer, self).get_fields()
        fields['username'].label = 'Access key ID'
        fields['username'].required = True

        fields['token'].label = 'Secret access key'
        fields['token'].required = True

        fields['region'].required = True
        fields['region'].initial = 'us-east-1'
        return fields


class ImageSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Image
        view_name = 'aws-image-detail'
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class SizeSerializer(six.with_metaclass(structure_serializers.PropertySerializerMetaclass,
                                        serializers.Serializer)):

    uuid = serializers.ReadOnlyField()
    url = serializers.SerializerMethodField()
    name = serializers.ReadOnlyField()
    cores = serializers.ReadOnlyField()
    ram = serializers.ReadOnlyField()
    disk = serializers.ReadOnlyField()

    class Meta(object):
        model = models.Size

    def get_url(self, size):
        return reverse('aws-size-detail', kwargs={'uuid': size.uuid}, request=self.context.get('request'))


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):

    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.AWSServiceProjectLink
        view_name = 'aws-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'aws-detail'},
        }


class InstanceSerializer(structure_serializers.VirtualMachineSerializer):

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='aws-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='aws-spl-detail',
        queryset=models.AWSServiceProjectLink.objects.all(),
        write_only=True)

    image = serializers.HyperlinkedRelatedField(
        view_name='aws-image-detail',
        lookup_field='uuid',
        queryset=models.Image.objects.all(),
        write_only=True)

    size = serializers.HyperlinkedRelatedField(
        view_name='aws-size-detail',
        lookup_field='uuid',
        queryset=SizeQueryset(),
        write_only=True)

    class Meta(structure_serializers.VirtualMachineSerializer.Meta):
        model = models.Instance
        view_name = 'aws-instance-detail'
        fields = structure_serializers.VirtualMachineSerializer.Meta.fields + (
            'image', 'size'
        )
        protected_fields = structure_serializers.VirtualMachineSerializer.Meta.protected_fields + (
            'image', 'size'
        )


class InstanceImportSerializer(structure_serializers.BaseResourceImportSerializer):

    class Meta(structure_serializers.BaseResourceImportSerializer.Meta):
        model = models.Instance
        view_name = 'aws-instance-detail'

    def create(self, validated_data):
        backend = self.context['service'].get_backend()
        try:
            instance = backend.get_instance(validated_data['backend_id'])
        except AWSBackendError:
            raise serializers.ValidationError(
                {'backend_id': "Can't find instance with ID %s" % validated_data['backend_id']})

        validated_data['name'] = instance['name']
        validated_data['external_ips'] = instance['external_ips']
        validated_data['cores'] = instance['cores']
        validated_data['ram'] = instance['ram']
        validated_data['disk'] = instance['disk']
        validated_data['created'] = instance['created']
        validated_data['state'] = models.Instance.States.ONLINE

        return super(InstanceImportSerializer, self).create(validated_data)
