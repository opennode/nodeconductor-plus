import logging

from django.utils import six
from libcloud.common.types import LibcloudError
from libcloud.compute.drivers.azure import AzureNodeDriver

from nodeconductor.core.utils import hours_in_month
from nodeconductor.structure import ServiceBackend, ServiceBackendError

from . import models


logger = logging.getLogger(__name__)


class AzureBackendError(ServiceBackendError):
    pass


class AzureBackend(object):

    def __init__(self, settings, **kwargs):
        backend_class = AzureDummyBackend if settings.dummy else AzureRealBackend
        self.backend = backend_class(settings, **kwargs)

    def __getattr__(self, name):
        return getattr(self.backend, name)


class AzureBaseBackend(ServiceBackend):

    def __init__(self, settings, cloud_service_name=None):
        self.settings = settings
        self.cloud_service_name = cloud_service_name
        self.manager = AzureNodeDriver(
            subscription_id=settings.username,
            key_file=settings.certificate.path if settings.certificate else None)

    def sync(self):
        self.pull_service_properties()


class AzureRealBackend(AzureBaseBackend):
    """ NodeConductor interface to Azure API.
        http://libcloud.readthedocs.org/en/latest/compute/drivers/azure.html
    """

    def ping(self):
        try:
            self.manager.list_locations()
        except LibcloudError:
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
        for backend_image in self.manager.list_images():
            cur_images.pop(backend_image.id, None)
            models.Image.objects.update_or_create(
                backend_id=backend_image.id,
                defaults={
                    'name': backend_image.name,
                })

        map(lambda i: i.delete(), cur_images.values())

    def pull_locations(self):
        cur_locations = {i.backend_id: i for i in models.Location.objects.all()}
        for backend_location in self.manager.list_locations():
            cur_locations.pop(backend_location.id, None)
            models.Location.objects.update_or_create(
                backend_id=backend_location.id,
                defaults={
                    'name': backend_location.name,
                })

        map(lambda i: i.delete(), cur_locations.values())

    def get_monthly_cost_estimate(self, vm):
        # calculate a price for current month based on hourly rate
        return float(self.get_vm(vm.backend_id).size.price) * hours_in_month()

    def get_vm(self, vm_id):
        try:
            vm = next(vm for vm in self.manager.list_nodes(self.cloud_service_name) if vm.id == vm_id)
            # XXX: libcloud seems doesn't map size properly
            vm.size = next(s for s in self.manager.list_sizes() if s.id == vm.extra['instance_size'])
            return vm
        except (StopIteration, LibcloudError) as e:
            six.reraise(AzureBackendError, e)

    def get_resources_for_import(self):
        if not self.cloud_service_name:
            raise AzureBackendError(
                "Resources could be fetched only for specific cloud service, "
                "please supply project_uuid query argument")

        cur_vms = models.VirtualMachine.objects.all().values_list('backend_id', flat=True)
        try:
            vms = self.manager.list_nodes(self.cloud_service_name)
        except LibcloudError as e:
            six.reraise(AzureBackendError, e)

        return [{
            'id': vm.id,
            'name': vm.name,
        } for vm in vms if vm.id not in cur_vms]


class AzureDummyBackend(AzureBaseBackend):
    pass
