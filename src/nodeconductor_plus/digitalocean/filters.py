from nodeconductor.structure import filters as structure_filters

from . import models


class ImageFilter(structure_filters.BaseServicePropertyFilter):

    class Meta(object):
        model = models.Image
        fields = structure_filters.BaseServicePropertyFilter.Meta.fields + ('distribution', 'type')
        order_by = (
            'distribution',
            'type',
            # desc
            '-distribution',
            '-type',
        )


class SizeFilter(structure_filters.BaseServicePropertyFilter):

    class Meta(object):
        model = models.Size
        fields = structure_filters.BaseServicePropertyFilter.Meta.fields + ('cores', 'ram', 'disk')
