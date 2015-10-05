import re
import logging

from django.utils import six
from libcloud.common.types import LibcloudError
from libcloud.compute.base import NodeAuthPassword
from libcloud.compute.drivers import azure

from nodeconductor.core.tasks import send_task
from nodeconductor.core.utils import hours_in_month
from nodeconductor.structure import ServiceBackend, ServiceBackendError

from . import models


logger = logging.getLogger(__name__)

SORTED_SIZES = sorted(azure.AZURE_COMPUTE_INSTANCE_TYPES.items(), key=lambda s: float(s[1]['price']))

# Build a list of size details supported by Azure
SIZE_DETAILS = [{
    'uuid': key,
    'name': val['name'],
    'cores': val['cores'],
    'ram': val['ram'],
    'disk': val['disk']
    } for key, val in SORTED_SIZES]

# Build a list of size choices supported by Azure
SIZES = tuple((k, v['name']) for k, v in SORTED_SIZES)

# libcloud doesn't match Visual Studio images properly
azure.WINDOWS_SERVER_REGEX = re.compile(
    azure.WINDOWS_SERVER_REGEX.pattern + '|VS-201[35]'
)


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
        self.deployment = 'production'
        self.location = 'Central US'
        if settings.options and 'location' in settings.options:
            self.location = settings.options['location']

        self.settings = settings
        self.cloud_service_name = cloud_service_name
        self.manager = azure.AzureNodeDriver(
            subscription_id=settings.username,
            key_file=settings.certificate.path if settings.certificate else None)

    def sync(self):
        self.pull_service_properties()

    def sync_link(self, service_project_link, is_initial=False):
        self.push_link(service_project_link)

    def provision(self, vm, region=None, image=None, size=None, username=None, password=None):
        size = next(s for s in self.manager.list_sizes() if s.id == size)
        vm.ram = size.ram
        vm.disk = size.disk
        vm.cores = size.extra['cores']
        vm.save()

        send_task('azure', 'provision')(
            vm.uuid.hex,
            backend_image_id=image.backend_id,
            backend_size_id=size.id,
            username=username,
            password=password)

    def destroy(self, vm):
        vm.schedule_deletion()
        vm.save()
        send_task('azure', 'destroy')(vm.uuid.hex)

    def restart(self, vm):
        vm.schedule_restarting()
        vm.save()
        send_task('azure', 'restart')(vm.uuid.hex)


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

    def get_monthly_cost_estimate(self, vm):
        # calculate a price for current month based on hourly rate
        return float(self.get_vm(vm.backend_id).size.price) * hours_in_month()

    def pull_service_properties(self):
        self.pull_images()

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

    def push_link(self, service_project_link):
        # XXX: must be less than 24 chars (due to libcloud bug actually)
        cloud_service_name = 'nc-%x' % service_project_link.project.uuid.node
        services = [s.service_name for s in self.manager.ex_list_cloud_services()]

        # XXX: consider creating storage account here too
        if cloud_service_name not in services:
            self.manager.ex_create_cloud_service(cloud_service_name, self.location)
            service_project_link.cloud_service_name = cloud_service_name
            service_project_link.save(update_fields=['cloud_service_name'])

    def reboot(self, vm):
        self.manager.reboot_node(
            self.get_vm(vm.backend_id),
            ex_cloud_service_name=self.cloud_service_name,
            ex_deployment_slot=self.deployment)

    def destroy_vm(self, vm):
        # XXX: it doesn't destroy attached storage
        self.manager.destroy_node(
            self.get_vm(vm.backend_id),
            ex_cloud_service_name=self.cloud_service_name,
            ex_deployment_slot=self.deployment)

    def provision_vm(self, vm, backend_image_id=None, backend_size_id=None,
                     username=None, password=None):
        try:
            backend_vm = self.manager.create_node(
                name=vm.name,
                size=self.get_size(backend_size_id),
                image=self.get_image(backend_image_id),
                ex_cloud_service_name=self.cloud_service_name,
                ex_deployment_slot=self.deployment,
                ex_custom_data=vm.user_data,
                ex_admin_user_id=username,
                auth=NodeAuthPassword(password))
        except LibcloudError as e:
            logger.exception('Failed to provision virtual machine %s', vm.name)
            six.reraise(AzureBackendError, e)

        vm.backend_id = backend_vm.id
        vm.save(update_fields=['backend_id'])
        return backend_vm

    def get_vm(self, vm_id):
        try:
            vm = next(vm for vm in self.manager.list_nodes(self.cloud_service_name) if vm.id == vm_id)
            # XXX: libcloud seems doesn't map size properly
            vm.size = self.get_size(vm.extra['instance_size'])
            return vm
        except (StopIteration, LibcloudError) as e:
            six.reraise(AzureBackendError, e)

    def get_size(self, size_id):
        try:
            return next(s for s in self.manager.list_sizes() if s.id == size_id)
        except (StopIteration, LibcloudError) as e:
            six.reraise(AzureBackendError, e)

    def get_image(self, image_id):
        try:
            return next(s for s in self.manager.list_images() if s.id == image_id)
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
