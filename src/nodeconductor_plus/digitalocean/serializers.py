from __future__ import unicode_literals

from rest_framework import serializers, exceptions

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


class RegionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta(object):
        model = models.Region
        view_name = 'digitalocean-region-detail'
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class SizeSerializer(serializers.HyperlinkedModelSerializer):

    class Meta(object):
        model = models.Size
        view_name = 'digitalocean-size-detail'
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class ServiceSerializer(structure_serializers.PermissionFieldFilteringMixin,
                        core_serializers.AugmentedSerializerMixin,
                        serializers.HyperlinkedModelSerializer):

    projects = structure_serializers.BasicProjectSerializer(many=True, read_only=True)
    customer_native_name = serializers.ReadOnlyField(source='customer.native_name')

    class Meta(object):
        model = models.DigitalOceanService
        view_name = 'digitalocean-detail'
        fields = (
            'uuid',
            'url',
            'name', 'projects', 'settings',
            'customer', 'customer_name', 'customer_native_name',
        )
        protected_fields = 'customer', 'settings'
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'customer': {'lookup_field': 'uuid'},
            'settings': {'lookup_field': 'uuid'},
        }

    def get_filtered_field_names(self):
        return 'customer',

    def get_related_paths(self):
        return 'customer',

    def validate(self, attrs):
        user = self.context['user']
        customer = attrs.get('customer') or self.instance.customer
        if not user.is_staff and not customer.has_user(user, structure_models.CustomerRole.OWNER):
            raise exceptions.PermissionDenied()

        return attrs


class ServiceProjectLinkSerializer(structure_serializers.PermissionFieldFilteringMixin,
                                   core_serializers.AugmentedSerializerMixin,
                                   serializers.HyperlinkedModelSerializer):

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
            'service': {'lookup_field': 'uuid', 'view_name': 'digitalocean-detail'},
            'project': {'lookup_field': 'uuid'},
        }

    def get_filtered_field_names(self):
        return 'project', 'service'

    def get_related_paths(self):
        return 'project', 'service'


class DropletSerializer(core_serializers.AugmentedSerializerMixin,
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
            'cores', 'ram', 'disk', 'transfer',
            'project_groups',
            'state',
            'created',
            'user_data',
        )
        view_name = 'digitalocean-droplet-detail'
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class DropletCreateSerializer(structure_serializers.PermissionFieldFilteringMixin,
                              serializers.HyperlinkedModelSerializer):

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-spl-detail',
        queryset=models.DigitalOceanServiceProjectLink.objects.filter(
            service__settings__type=structure_models.ServiceSettings.Types.DigitalOcean),
        required=True,
        write_only=True)

    region = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-region-detail',
        lookup_field='uuid',
        queryset=models.Region.objects.all().select_related('settings'),
        required=True,
        write_only=True)

    image = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-image-detail',
        lookup_field='uuid',
        queryset=models.Image.objects.all().select_related('settings'),
        required=True,
        write_only=True)

    size = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-size-detail',
        lookup_field='uuid',
        queryset=models.Size.objects.all().select_related('settings'),
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
            'name', 'description', 'service_project_link',
            'region', 'image', 'size', 'ssh_public_key', 'user_data',
        )

    def get_filtered_field_names(self):
        return 'service_project_link',

    def get_fields(self):
        user = self.context['user']
        fields = super(DropletCreateSerializer, self).get_fields()
        fields['ssh_public_key'].queryset = fields['ssh_public_key'].queryset.filter(user=user)
        return fields

    def validate(self, attrs):
        settings = attrs['service_project_link'].service.settings
        region = attrs['region']
        image = attrs['image']
        size = attrs['size']

        if any([region.settings != settings, image.settings != settings, size.settings != settings]):
            raise serializers.ValidationError(
                "Region, image and size must belong to the same service settings.")

        if not image.regions.filter(pk=region.pk).exists():
            raise serializers.ValidationError("Image is missed in region %s" % region)

        if not size.regions.filter(pk=region.pk).exists():
            raise serializers.ValidationError("Size is missed in region %s" % region)

        return attrs

    def create(self, validated_data):
        data = validated_data.copy()
        # Remove `virtual` properties which ain't actually belong to the model
        for prop in ('region', 'image', 'size', 'ssh_public_key'):
            if prop in data:
                del data[prop]

        return super(DropletCreateSerializer, self).create(data)
