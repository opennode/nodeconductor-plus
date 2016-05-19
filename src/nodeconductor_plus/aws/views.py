import six
from rest_framework import viewsets

from nodeconductor.core.views import StateExecutorViewSet
from nodeconductor.structure import views as structure_views

from . import filters, models, serializers, executors


class AmazonServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.AWSService.objects.all()
    serializer_class = serializers.ServiceSerializer
    import_serializer_class = serializers.InstanceImportSerializer

    def get_import_context(self):
        return {'resource_type': self.request.query_params.get('resource_type')}

    def get_serializer_class(self):
        from nodeconductor.structure import SupportedServices

        if self.request.method == 'POST':
            resource_type = self.request.data.get('type')
            if resource_type == SupportedServices.get_name_for_model(models.Instance):
                return serializers.InstanceImportSerializer
            elif resource_type == SupportedServices.get_name_for_model(models.Volume):
                return serializers.VolumeImportSerializer
        return super(AmazonServiceViewSet, self).get_serializer_class()


class AmazonServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.AWSServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class RegionViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    lookup_field = 'uuid'


class ImageViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    filter_class = filters.ImageFilter
    lookup_field = 'uuid'


class SizeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Size.objects.all()
    serializer_class = serializers.SizeSerializer
    filter_class = filters.SizeFilter
    lookup_field = 'uuid'


class InstanceViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Instance.objects.all()
    serializer_class = serializers.InstanceSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            region=serializer.validated_data['region'],
            image=serializer.validated_data['image'],
            size=serializer.validated_data['size'],
            ssh_key=serializer.validated_data.get('ssh_public_key'))


class VolumeViewSet(six.with_metaclass(structure_views.ResourceViewMetaclass,
                                       structure_views.ResourceViewMixin,
                                       StateExecutorViewSet)):
    queryset = models.Volume.objects.all()
    serializer_class = serializers.VolumeSerializer
    create_executor = executors.VolumeCreateExecutor
    delete_executor = executors.VolumeDeleteExecutor

    # TODO: Attach & detach volume to instance
