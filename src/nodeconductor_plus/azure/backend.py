import os.path
import logging

from django.conf import settings as django_settings

# TODO: Replace it with libcloud AzureNodeDriver as soon as its support released
# from libcloud.compute.drivers.azure import AzureNodeDriver
from ssl import SSLError
from azure import WindowsAzureError
from azure.servicemanagement import ServiceManagementService
from nodeconductor.structure import ServiceBackend, ServiceBackendError

from . import models


logger = logging.getLogger(__name__)


class AzureBackendError(ServiceBackendError):
    pass


class AzureBackend(object):

    def __init__(self, settings):
        backend_class = AzureDummyBackend if settings.dummy else AzureRealBackend
        self.backend = backend_class(settings)

    def __getattr__(self, name):
        return getattr(self.backend, name)


class AzureBaseBackend(ServiceBackend):

    def __init__(self, settings):
        self.settings = settings
        key_file = settings.token
        if not key_file.startswith('/'):
            key_file = os.path.join(django_settings.BASE_DIR, key_file)

        self.manager = ServiceManagementService(settings.username, key_file)

    def sync(self):
        self.pull_service_properties()


class AzureRealBackend(AzureBaseBackend):
    """ NodeConductor interface to Azure API.
        https://libcloud.apache.org/
        https://github.com/Azure/azure-sdk-for-python
    """

    def ping(self):
        try:
            self.manager.list_locations()
        except (WindowsAzureError, SSLError):
            return False
        else:
            return True

    def ping_resource(self, instance):
        try:
            self.get_vm(instance.backend_id)
        except AzureBackendError:
            return False
        else:
            return True

    def pull_service_properties(self):
        self.pull_images()
        self.pull_locations()

    def pull_images(self):
        cur_images = {i.backend_id: i for i in models.Image.objects.all()}
        for backend_image in self.manager.list_vm_images().vm_images:
            cur_images.pop(backend_image.name, None)
            models.Image.objects.update_or_create(
                backend_id=backend_image.name,
                defaults={
                    'name': backend_image.label,
                })

        map(lambda i: i.delete(), cur_images.values())

    def pull_locations(self):
        cur_locations = {i.backend_id: i for i in models.Location.objects.all()}
        for backend_location in self.manager.list_locations().locations:
            cur_locations.pop(backend_location.name, None)
            models.Location.objects.update_or_create(
                backend_id=backend_location.name,
                defaults={
                    'name': backend_location.display_name,
                })

        map(lambda i: i.delete(), cur_locations.values())

    def get_vm(self, vm_name):
        try:
            return self.manager.get_hosted_service_properties(vm_name)
        except WindowsAzureError as e:
            six.reraise(AzureBackendError, e)

    def get_resources_for_import(self):
        cur_vms = models.VirtualMachine.objects.all().values_list('backend_id', flat=True)
        return [{
            'id': vm.service_name,
            'name': vm.service_name,
            'created': vm.hosted_service_properties.date_created,
            'location': vm.hosted_service_properties.location,
        } for vm in self.manager.list_hosted_services().hosted_services
            if vm.service_name not in cur_vms]


class AzureDummyBackend(AzureBaseBackend):
    pass
