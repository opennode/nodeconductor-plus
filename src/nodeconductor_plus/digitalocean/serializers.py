from __future__ import unicode_literals

from rest_framework import serializers

from nodeconductor.core import serializers as core_serializers
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
