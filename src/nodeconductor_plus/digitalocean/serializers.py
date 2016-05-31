from __future__ import unicode_literals

import re

from django.utils import dateparse
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from nodeconductor.structure import serializers as structure_serializers

from . import models
from .backend import DigitalOceanBackendError


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_ACCOUNT_FIELDS = {
        'token': '',
    }

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.DigitalOceanService
        view_name = 'digitalocean-detail'

    def get_fields(self):
        fields = super(ServiceSerializer, self).get_fields()
        fields['token'].label = 'Access token'
        return fields


class RegionSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Region
        view_name = 'digitalocean-region-detail'
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class ImageSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Image
        view_name = 'digitalocean-image-detail'
        fields = ('url', 'uuid', 'name', 'distribution', 'type', 'regions')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }

    regions = RegionSerializer(many=True, read_only=True)


class SizeSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Size
        view_name = 'digitalocean-size-detail'
        fields = ('url', 'uuid', 'name', 'cores', 'ram', 'disk', 'transfer', 'regions')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }

    regions = RegionSerializer(many=True, read_only=True)


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):

    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.DigitalOceanServiceProjectLink
        view_name = 'digitalocean-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'digitalocean-detail'},
        }


class DropletSerializer(structure_serializers.VirtualMachineSerializer):

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='digitalocean-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-spl-detail',
        queryset=models.DigitalOceanServiceProjectLink.objects.all())

    region = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-region-detail',
        lookup_field='uuid',
        queryset=models.Region.objects.all(),
        write_only=True)

    image = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-image-detail',
        lookup_field='uuid',
        queryset=models.Image.objects.all(),
        write_only=True)

    size = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-size-detail',
        lookup_field='uuid',
        queryset=models.Size.objects.all(),
        write_only=True)

    class Meta(structure_serializers.VirtualMachineSerializer.Meta):
        model = models.Droplet
        view_name = 'digitalocean-droplet-detail'
        fields = structure_serializers.VirtualMachineSerializer.Meta.fields + (
            'region', 'image', 'size',
        )
        protected_fields = structure_serializers.VirtualMachineSerializer.Meta.protected_fields + (
            'region', 'image', 'size',
        )

    def validate(self, attrs):
        if not self.instance:
            region = attrs['region']
            image = attrs['image']
            size = attrs['size']

            if not re.match(r'[a-zA-Z0-9.-]+$', attrs['name']):
                raise serializers.ValidationError(
                    "Only valid hostname characters are allowed. (a-z, A-Z, 0-9, . and -)")

            if not attrs.get('ssh_public_key') and image.is_ssh_key_mandatory:
                raise serializers.ValidationError("SSH public key is required for this image")

            if not image.regions.filter(pk=region.pk).exists():
                raise serializers.ValidationError("Image is missing in region %s" % region)

            if not size.regions.filter(pk=region.pk).exists():
                raise serializers.ValidationError("Size is missing in region %s" % region)

        return attrs


class DropletImportSerializer(structure_serializers.BaseResourceImportSerializer):

    class Meta(structure_serializers.BaseResourceImportSerializer.Meta):
        model = models.Droplet
        view_name = 'digitalocean-droplet-detail'

    def create(self, validated_data):
        backend = self.context['service'].get_backend()
        try:
            droplet = backend.get_droplet(validated_data['backend_id'])
        except DigitalOceanBackendError:
            raise serializers.ValidationError(
                {'backend_id': "Can't find droplet with ID %s" % validated_data['backend_id']})

        validated_data['name'] = droplet.name
        validated_data['cores'] = droplet.vcpus
        validated_data['ram'] = droplet.memory
        validated_data['disk'] = backend.gb2mb(droplet.disk)
        validated_data['transfer'] = backend.tb2mb(droplet.size['transfer'])
        validated_data['external_ips'] = droplet.ip_address
        validated_data['created'] = dateparse.parse_datetime(droplet.created_at)
        validated_data['state'] = models.Droplet.States.ONLINE if droplet.status == 'active' else \
            models.Droplet.States.OFFLINE

        return super(DropletImportSerializer, self).create(validated_data)


class DropletResizeSerializer(serializers.Serializer):
    size = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-size-detail',
        lookup_field='uuid',
        queryset=models.Size.objects.all(),
        write_only=True)
    disk = serializers.BooleanField(required=True)

    def get_fields(self):
        fields = super(DropletResizeSerializer, self).get_fields()
        field = fields['size']
        field.value_field = 'url'
        field.display_name_field = 'name'
        return fields

    class Meta:
        fields = 'size', 'disk'

    def validate_size(self, value):
        if value:
            if self.is_same_size(value):
                raise ValidationError("New size is the same. Please select another one.")

            if value.disk < self.instance.disk:
                raise ValidationError("Disk sizes are not allowed to be decreased through a resize operation.")
        return value

    def is_same_size(self, new_size):
        return new_size.disk == self.instance.disk and \
               new_size.cores == self.instance.cores and \
               new_size.ram == self.instance.ram
