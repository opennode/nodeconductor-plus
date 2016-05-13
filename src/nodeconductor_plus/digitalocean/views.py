from __future__ import unicode_literals

from rest_framework.decorators import detail_route

from nodeconductor.structure import views as structure_views

from . import models, serializers, log, filters


class DigitalOceanServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.DigitalOceanService.objects.all()
    serializer_class = serializers.ServiceSerializer
    import_serializer_class = serializers.DropletImportSerializer


class DigitalOceanServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.DigitalOceanServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class ImageViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    filter_class = filters.ImageFilter
    lookup_field = 'uuid'


class RegionViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    lookup_field = 'uuid'

    def get_queryset(self):
        return models.Region.objects.order_by('name')


class SizeViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Size.objects.all()
    serializer_class = serializers.SizeSerializer
    filter_class = filters.SizeFilter
    lookup_field = 'uuid'


class DropletViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Droplet.objects.all()
    serializer_class = serializers.DropletSerializer

    def get_serializer_class(self):
        if self.action == 'resize':
            return serializers.DropletResizeSerializer
        return super(DropletViewSet, self).get_serializer_class()

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            region=serializer.validated_data['region'],
            image=serializer.validated_data['image'],
            size=serializer.validated_data['size'],
            ssh_key=serializer.validated_data.get('ssh_public_key'))

    @detail_route(methods=['post'])
    @structure_views.safe_operation(valid_state=models.Droplet.States.OFFLINE)
    def resize(self, request, instance, uuid=None):
        """
        To resize droplet, submit a **POST** request to the instance URL, specifying URI of a target size.
        Note, that instance must be OFFLINE. Example of a valid request:

        .. code-block:: http

            POST /api/digitalocean-droplets/6c9b01c251c24174a6691a1f894fae31/resize/ HTTP/1.1
            Content-Type: application/json
            Accept: application/json
            Authorization: Token c84d653b9ec92c6cbac41c706593e66f567a7fa4
            Host: example.com

            {
                "size": "http://example.com/api/digitalocean-sizes/1ee385bc043249498cfeb8c7e3e079f0/"
            }
        """
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        size = serializer.validated_data.get('size')
        backend = instance.get_backend()
        backend.resize(instance, size)

        log.event_logger.droplet_resize.info(
            'Droplet {droplet_name} has been scheduled to resize.',
            event_type='droplet_resize_scheduled',
            event_context={'droplet': instance, 'size': size}
        )
