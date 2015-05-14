from __future__ import unicode_literals

from rest_framework import serializers

from nodeconductor.core import serializers as core_serializers
from nodeconductor.structure import serializers as structure_serializers

from . import models


class ImageSerializer(serializers.ModelSerializer):

    class Meta(object):
        model = models.Image
        fields = ('uuid', 'name')


class ServiceSerializer(structure_serializers.PermissionFieldFilteringMixin,
                        core_serializers.AugmentedSerializerMixin,
                        serializers.HyperlinkedModelSerializer):
    images = ImageSerializer(many=True, read_only=True)
    projects = structure_serializers.BasicProjectSerializer(many=True, read_only=True)
    auth_token = serializers.CharField(write_only=True)
    customer_native_name = serializers.ReadOnlyField(source='customer.native_name')

    class Meta(object):
        model = models.DigitalOceanService
        fields = (
            'uuid',
            'url',
            'name',
            'customer', 'customer_name', 'customer_native_name',
            'projects', 'images', 'auth_token', 'dummy'
        )
        readonly_fields = 'customer',
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'customer': {'lookup_field': 'uuid'},
        }

    def get_filtered_field_names(self):
        return 'customer',

    def get_related_paths(self):
        return 'customer',
