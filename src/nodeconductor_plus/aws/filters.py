import django_filters

from nodeconductor.structure import filters as structure_filters

from . import models


class ImageFilter(structure_filters.BaseServicePropertyFilter):

    class Meta():
        model = models.Image
        fields = structure_filters.BaseServicePropertyFilter.Meta.fields + ('region',)

    region = django_filters.CharFilter(name='region__uuid')


class SizeFilter(structure_filters.BaseServicePropertyFilter):

    class Meta():
        model = models.Size
        fields = structure_filters.BaseServicePropertyFilter.Meta.fields + ('region',)

    region = django_filters.CharFilter(name='regions__uuid')
