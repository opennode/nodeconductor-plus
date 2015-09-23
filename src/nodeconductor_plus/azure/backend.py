import logging

from django.utils import six

# TODO: Replace it with libcloud AzureNodeDriver as soon as its support released
# from libcloud.compute.drivers.azure import AzureNodeDriver
from ssl import SSLError
from azure import WindowsAzureError
from azure.servicemanagement import ServiceManagementService
from nodeconductor.core.utils import hours_in_month
from nodeconductor.structure import ServiceBackend, ServiceBackendError

from . import models


logger = logging.getLogger(__name__)


# Prices are for Linux instances in East US data center. To see what pricing will actually be, visit:
# http://azure.microsoft.com/en-gb/pricing/details/virtual-machines/
AZURE_COMPUTE_INSTANCE_PRICES = {
    'ExtraSmall': 0.0211,       # AO
    'Small': 0.0633,            # A1
    'Medium': 0.1266,           # A2
    'Large': 0.2531,            # A3
    'ExtraLarge': 0.5062,       # A4
    'A5': 0.2637,
    'A6': 0.5273,
    'A7': 1.0545,
    'A8': 2.0774,
    'A9': 4.7137,
    'A10': 1.2233,
    'A11': 2.1934,
    'Standard_D1': 0.0992,
    'Standard_D2': 0.1983,
    'Standard_D3': 0.3965,
    'Standard_D4': 0.7930,
    'Standard_D11': 0.251,
    'Standard_D12': 0.502,
    'Standard_D13': 0.9038,
    'Standard_D14': 1.6261,
}


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
        cert_file = settings.certificate.path if settings.certificate else None
        self.manager = ServiceManagementService(settings.username, cert_file)

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

    def get_monthly_cost_estimate(self, vm):
        try:
            info = self.manager.get_deployment_by_slot(vm.backend_id, 'production')
        except (WindowsAzureError, SSLError) as e:
            six.reraise(AzureBackendError, e)

        size = next(i.instance_size for i in info.role_instance_list.role_instances
                    if i.instance_name == vm.backend_id)

        # calculate a price for current month based on hourly rate
        return AZURE_COMPUTE_INSTANCE_PRICES.get(size) * hours_in_month()

    def get_vm(self, vm_name):
        try:
            return self.manager.get_hosted_service_properties(vm_name)
        except (WindowsAzureError, SSLError) as e:
            six.reraise(AzureBackendError, e)

    def get_resources_for_import(self):
        cur_vms = models.VirtualMachine.objects.all().values_list('backend_id', flat=True)
        try:
            vms = self.manager.list_hosted_services().hosted_services
        except (WindowsAzureError, SSLError) as e:
            six.reraise(AzureBackendError, e)

        return [{
            'id': vm.service_name,
            'name': vm.service_name,
            'created': vm.hosted_service_properties.date_created,
            'location': vm.hosted_service_properties.location,
        } for vm in vms if vm.service_name not in cur_vms]


class AzureDummyBackend(AzureBaseBackend):
    pass
