from __future__ import unicode_literals

import re

from rest_framework import serializers

from nodeconductor.core import models as core_models
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


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_TYPE = structure_models.ServiceSettings.Types.DigitalOcean

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.DigitalOceanService
        view_name = 'digitalocean-detail'


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):

    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.DigitalOceanServiceProjectLink
        view_name = 'digitalocean-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'digitalocean-detail'},
        }


class DropletSerializer(structure_serializers.BaseResourceSerializer):

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='digitalocean-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-spl-detail',
        queryset=models.DigitalOceanServiceProjectLink.objects.filter(
            service__settings__type=structure_models.ServiceSettings.Types.DigitalOcean),
        write_only=True)

    region = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-region-detail',
        lookup_field='uuid',
        queryset=models.Region.objects.all().select_related('settings'),
        write_only=True)

    image = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-image-detail',
        lookup_field='uuid',
        queryset=models.Image.objects.all().select_related('settings'),
        write_only=True)

    size = serializers.HyperlinkedRelatedField(
        view_name='digitalocean-size-detail',
        lookup_field='uuid',
        queryset=models.Size.objects.all().select_related('settings'),
        write_only=True)

    ssh_public_key = serializers.HyperlinkedRelatedField(
        view_name='sshpublickey-detail',
        lookup_field='uuid',
        queryset=core_models.SshPublicKey.objects.all(),
        required=False,
        write_only=True)

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.Droplet
        view_name = 'digitalocean-droplet-detail'
        read_only_fields = ('start_time', 'cores', 'ram', 'disk', 'transfer')
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'cores', 'ram', 'disk', 'transfer',
            'region', 'image', 'size', 'ssh_public_key',
            'user_data',
        )

    def get_fields(self):
        user = self.context['user']
        fields = super(DropletSerializer, self).get_fields()
        fields['ssh_public_key'].queryset = fields['ssh_public_key'].queryset.filter(user=user)
        return fields

    def validate(self, attrs):
        settings = attrs['service_project_link'].service.settings
        region = attrs['region']
        image = attrs['image']
        size = attrs['size']

        if not re.match(r'[a-z0-9-]+\.[a-z0-9]{1,4}', attrs['name']):
            raise serializers.ValidationError(
                "Only valid hostname characters are allowed. (a-z, A-Z, 0-9, . and -)")

        if any([region.settings != settings, image.settings != settings, size.settings != settings]):
            raise serializers.ValidationError(
                "Region, image and size must belong to the same service settings.")

        if not image.regions.filter(pk=region.pk).exists():
            raise serializers.ValidationError("Image is missed in region %s" % region)

        if not size.regions.filter(pk=region.pk).exists():
            raise serializers.ValidationError("Size is missed in region %s" % region)

        return attrs
