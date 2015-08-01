from rest_framework import viewsets

from nodeconductor.structure import views as structure_views

from . import models, serializers


class AzureServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.AzureService.objects.all()
    serializer_class = serializers.ServiceSerializer
    import_serializer_class = serializers.VirtualMachineImportSerializer


class AzureServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.AzureServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class ImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    lookup_field = 'uuid'


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer
    lookup_field = 'uuid'


class VirtualMachineViewSet(structure_views.BaseResourceViewSet):
    queryset = models.VirtualMachine.objects.all()
    serializer_class = serializers.VirtualMachineSerializer
