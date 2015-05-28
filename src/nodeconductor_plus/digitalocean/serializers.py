from __future__ import unicode_literals

from rest_framework import serializers

from nodeconductor.core import models as core_models
from nodeconductor.core import serializers as core_serializers
from nodeconductor.core.fields import MappedChoiceField
from nodeconductor.structure import models as structure_models
from nodeconductor.structure import serializers as structure_serializers

from . import models


class ImageSerializer(serializers.HyperlinkedModelSerializer):

    class Meta(object):
        model = models.Image
        view_name = 'digitalocean-image-detail'
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class RegionSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.Region
        view_name = 'digitalocean-region-detail'
        fields = ('uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class SizeSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.Size
        view_name = 'digitalocean-size-detail'
        fields = ('uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class ServiceSerializer(structure_serializers.PermissionFieldFilteringMixin,
                        core_serializers.AugmentedSerializerMixin,
                        serializers.HyperlinkedModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    projects = structure_serializers.BasicProjectSerializer(many=True, read_only=True)
    customer_native_name = serializers.ReadOnlyField(source='customer.native_name')

    class Meta(object):
        model = models.DigitalOceanService
        view_name = 'digitalocean-detail'
        fields = (
            'uuid',
            'url',
            'name',
            'customer', 'customer_name', 'customer_native_name',
            'projects', 'images', 'auth_token', 'dummy'
        )
        protected_fields = 'customer', 'auth_token'
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'customer': {'lookup_field': 'uuid'},
        }

    def get_filtered_field_names(self):
        return 'customer',

    def get_related_paths(self):
        return 'customer',


class ServiceProjectLinkSerializer(structure_serializers.PermissionFieldFilteringMixin,
                                   core_serializers.AugmentedSerializerMixin,
                                   serializers.HyperlinkedModelSerializer):

    service = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-detail',
        lookup_field='uuid',
        queryset=models.DigitalOceanService.objects.all(),
        required=True)

    state = MappedChoiceField(
        choices=[(v, k) for k, v in core_models.SynchronizationStates.CHOICES],
        choice_mappings={v: k for k, v in core_models.SynchronizationStates.CHOICES},
        read_only=True)

    class Meta(object):
        model = models.DigitalOceanServiceProjectLink
        fields = (
            'url',
            'project', 'project_name', 'project_uuid',
            'service', 'service_name', 'service_uuid',
            'state',
        )
        view_name = 'digitalocean-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid'},
            'project': {'lookup_field': 'uuid'},
        }

    def get_filtered_field_names(self):
        return 'project', 'service'

    def get_related_paths(self):
        return 'project', 'service'


class ResourceSerializer(core_serializers.AugmentedSerializerMixin,
                         serializers.HyperlinkedModelSerializer):

    state = serializers.ReadOnlyField(source='get_state_display')
    project_groups = structure_serializers.BasicProjectGroupSerializer(
        source='service_project_link.project.project_groups', many=True, read_only=True)

    project = serializers.HyperlinkedRelatedField(
        source='service_project_link.project',
        view_name='project-detail',
        read_only=True,
        lookup_field='uuid')

    project_name = serializers.ReadOnlyField(source='service_project_link.project.name')
    project_uuid = serializers.ReadOnlyField(source='service_project_link.project.uuid')

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='digitalocean-detail',
        read_only=True,
        lookup_field='uuid')

    service_name = serializers.ReadOnlyField(source='service_project_link.service.name')
    service_uuid = serializers.ReadOnlyField(source='service_project_link.service.uuid')

    customer = serializers.HyperlinkedRelatedField(
        source='service_project_link.project.customer',
        view_name='customer-detail',
        read_only=True,
        lookup_field='uuid')

    customer_name = serializers.ReadOnlyField(source='service_project_link.project.customer.name')
    customer_abbreviation = serializers.ReadOnlyField(source='service_project_link.project.customer.abbreviation')
    customer_native_name = serializers.ReadOnlyField(source='service_project_link.project.customer.native_name')

    created = serializers.DateTimeField()

    class Meta(object):
        model = models.Droplet
        fields = (
            'url', 'uuid', 'name', 'description', 'start_time',
            'service', 'service_name', 'service_uuid',
            'project', 'project_name', 'project_uuid',
            'customer', 'customer_name', 'customer_native_name', 'customer_abbreviation',
            'cores', 'ram', 'disk', 'bandwidth',
            'project_groups',
            'state',
            'created',
            'user_data',
        )
        view_name = 'digitalocean-resource-detail'
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class ResourceCreateSerializer(structure_serializers.PermissionFieldFilteringMixin,
                               serializers.HyperlinkedModelSerializer):

    project = serializers.HyperlinkedRelatedField(
        view_name='project-detail',
        lookup_field='uuid',
        queryset=structure_models.Project.objects.all(),
        required=True,
        write_only=True)

    region = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-region-detail',
        lookup_field='uuid',
        queryset=models.Region.objects.all(),
        required=True,
        write_only=True)

    image = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-image-detail',
        lookup_field='uuid',
        queryset=models.Image.objects.all(),
        required=True,
        write_only=True)

    size = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-size-detail',
        lookup_field='uuid',
        queryset=models.Size.objects.all(),
        required=True,
        write_only=True)

    ssh_public_key = serializers.HyperlinkedRelatedField(
        view_name='sshpublickey-detail',
        lookup_field='uuid',
        queryset=core_models.SshPublicKey.objects.all(),
        required=False,
        write_only=True)

    class Meta(object):
        model = models.Droplet
        fields = (
            'url', 'uuid',
            'name', 'description',
            'project', 'region', 'image', 'size',
            'ssh_public_key', 'user_data',
        )
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }

    def get_filtered_field_names(self):
        return 'project', 'region', 'image', 'size'

    def get_fields(self):
        user = self.context['view'].request.user
        fields = super(ResourceCreateSerializer, self).get_fields()
        fields['ssh_public_key'].queryset = fields['ssh_public_key'].queryset.filter(user=user)
        return fields

    def to_internal_value(self, data):
        validated_data = super(ResourceCreateSerializer, self).to_internal_value(data)
        try:
            validated_data['service_project_link'] = \
                models.DigitalOceanServiceProjectLink.objects.get(
                    project=validated_data['project'],
                    service=validated_data['image'].service)
        except models.DigitalOceanServiceProjectLink.DoesNotExist:
            raise serializers.ValidationError({"image": "Image is not within project's service."})

        return validated_data

    def validate(self, attrs):
        region = attrs['region']
        image = attrs['image']
        size = attrs['size']

        if region.service != image.service or region.service != size.service:
            raise serializers.ValidationError(
                "Region, image and size must belong to the same service.")

        if not image.regions.filter(pk=region.pk).exists():
            raise serializers.ValidationError("Image is missed in region %s" % region)

        if not size.regions.filter(pk=region.pk).exists():
            raise serializers.ValidationError("Size is missed in region %s" % region)

        return attrs

    def create(self, validated_data):
        data = validated_data.copy()
        # Remove `virtual` properties which ain't actually belong to the model
        for prop in ('project', 'region', 'image', 'size', 'ssh_public_key'):
            if prop in data:
                del data[prop]

        return super(ResourceCreateSerializer, self).create(data)
