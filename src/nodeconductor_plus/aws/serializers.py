from rest_framework import serializers

from nodeconductor.structure import serializers as structure_serializers

from . import models
from .backend import AWSBackendError


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_ACCOUNT_FIELDS = {
        'username': '',
        'token': '',
    }

    SERVICE_ACCOUNT_EXTRA_FIELDS = {
        'images_regex': ''
    }

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.AWSService
        view_name = 'aws-detail'

    def get_fields(self):
        fields = super(ServiceSerializer, self).get_fields()
        fields['username'].label = 'Access key ID'
        fields['username'].required = True

        fields['token'].label = 'Secret access key'
        fields['token'].required = True

        fields['images_regex'].help_text = 'Regular expression to limit images list'

        return fields


class RegionSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Region
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'aws-region-detail'}
        }


class ImageSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Image
        fields = ('url', 'uuid', 'name', 'region')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'aws-image-detail'}
        }

    region = RegionSerializer(read_only=True)


class SizeSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Size
        fields = ('url', 'uuid', 'name', 'cores', 'ram', 'disk', 'regions', 'description')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'aws-size-detail'}
        }

    # AWS expose a more technical backend_id as a name. AWS's short codes are more popular
    name = serializers.ReadOnlyField(source='backend_id')
    description = serializers.ReadOnlyField(source='name')
    regions = RegionSerializer(many=True, read_only=True)


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
        queryset=models.AWSServiceProjectLink.objects.all())

    region = serializers.HyperlinkedRelatedField(
        view_name='aws-region-detail',
        lookup_field='uuid',
        queryset=models.Region.objects.all(),
        write_only=True)

    image = serializers.HyperlinkedRelatedField(
        view_name='aws-image-detail',
        lookup_field='uuid',
        queryset=models.Image.objects.all(),
        write_only=True)

    size = serializers.HyperlinkedRelatedField(
        view_name='aws-size-detail',
        lookup_field='uuid',
        queryset=models.Size.objects.all(),
        write_only=True)

    class Meta(structure_serializers.VirtualMachineSerializer.Meta):
        model = models.Instance
        view_name = 'aws-instance-detail'
        fields = structure_serializers.VirtualMachineSerializer.Meta.fields + (
            'region', 'image', 'size'
        )
        protected_fields = structure_serializers.VirtualMachineSerializer.Meta.protected_fields + (
            'region', 'image', 'size'
        )

    def validate(self, attrs):
        region = attrs['region']
        image = attrs['image']
        size = attrs['size']

        if image.region != region:
            raise serializers.ValidationError("Image is missing in region %s" % region.name)

        if not size.regions.filter(pk=region.pk).exists():
            raise serializers.ValidationError("Size is missing in region %s" % region.name)

        return attrs


class InstanceImportSerializer(structure_serializers.BaseResourceImportSerializer):

    class Meta(structure_serializers.BaseResourceImportSerializer.Meta):
        model = models.Instance
        view_name = 'aws-instance-detail'

    def create(self, validated_data):
        backend = self.context['service'].get_backend()
        try:
            region, instance = backend.find_instance(validated_data['backend_id'])
        except AWSBackendError:
            raise serializers.ValidationError(
                {'backend_id': "Can't find instance with ID %s" % validated_data['backend_id']})

        validated_data['name'] = instance['name']
        validated_data['external_ips'] = instance['external_ips']
        validated_data['cores'] = instance['cores']
        validated_data['ram'] = instance['ram']
        validated_data['disk'] = instance['disk']
        validated_data['created'] = instance['created']
        validated_data['state'] = instance['state']
        validated_data['region'] = region

        return super(InstanceImportSerializer, self).create(validated_data)
