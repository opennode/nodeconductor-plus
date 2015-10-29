import re
import time
import logging
import collections

from django.db import IntegrityError
from django.utils import six
from libcloud.common.types import LibcloudError
from libcloud.compute.base import NodeAuthPassword
from libcloud.compute.drivers import azure

from nodeconductor.core.tasks import send_task
from nodeconductor.core.utils import hours_in_month
from nodeconductor.structure import ServiceBackend, ServiceBackendError, ServiceBackendNotImplemented

from . import models


logger = logging.getLogger(__name__)

# libcloud doesn't match Visual Studio images properly
azure.WINDOWS_SERVER_REGEX = re.compile(
    azure.WINDOWS_SERVER_REGEX.pattern + '|VS-201[35]'
)

# there's a hope libcloud will implement this method in further releases
azure.AzureNodeDriver.ex_list_storage_services = lambda self: \
    self._perform_get(self._get_path('services', 'storageservices'), StorageServices)


class SizeQueryset(object):
    def __init__(self):
        self.items = []
        for val in azure.AZURE_COMPUTE_INSTANCE_TYPES.values():
            self.items.append(SizeQueryset.Size(uuid=val['id'],
                                                pk=val['id'],
                                                name=val['name'],
                                                cores=isinstance(val['cores'], int) and val['cores'] or 1,
                                                ram=val['ram'],
                                                disk=ServiceBackend.gb2mb(val['disk']),
                                                price=float(val['price'])))

        self.items = list(sorted(self.items, key=lambda s: s.price))

    def __len__(self):
        return len(self.items)

    def __getitem__(self, key):
        return self.items[key]

    def all(self):
        return self.items

    def get(self, uuid):
        for item in self.items:
            if item.uuid == uuid:
                return item
        raise ValueError

    class Size(collections.namedtuple('Size', ('uuid', 'pk', 'name', 'cores', 'ram', 'disk', 'price'))):
        def __str__(self):
            return self.name


class StorageServiceProperties(azure.WindowsAzureData):

    def __init__(self):
        self.description = ''
        self.location = ''
        self.affinity_group = ''
        self.label = azure._Base64String()
        self.status = ''
        self.createion_time = ''


class StorageService(azure.WindowsAzureData):
    _repr_attributes = [
        'service_name',
        'url'
    ]

    def __init__(self):
        self.url = ''
        self.service_name = ''
        self.storage_service_properties = StorageServiceProperties()


class StorageServices(azure.WindowsAzureDataTypedList, azure.ReprMixin):
    list_type = StorageService

    _repr_attributes = [
        'items'
    ]


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

    # Lazy init
    @property
    def manager(self):
        if not hasattr(self, '_manager'):
            self._manager = azure.AzureNodeDriver(
                subscription_id=self.settings.username,
                key_file=self.settings.certificate.path if self.settings.certificate else None)
        return self._manager

    def sync(self):
        self.pull_service_properties()

    def sync_link(self, service_project_link, is_initial=False):
        self.push_link(service_project_link)

    def remove_link(self, service_project_link):
        # TODO: this should remove storage and cloud service
        raise ServiceBackendNotImplemented

    def provision(self, vm, region=None, image=None, size=None, username=None, password=None):
        vm.ram = size.ram
        vm.disk = size.disk
        vm.cores = size.cores
        vm.save()

        send_task('azure', 'provision')(
            vm.uuid.hex,
            backend_image_id=image.backend_id,
            backend_size_id=size.pk,
            username=username,
            password=password)

    def destroy(self, vm):
        vm.schedule_deletion()
        vm.save()
        send_task('azure', 'destroy')(vm.uuid.hex)

    def start(self, vm):
        vm.schedule_starting()
        vm.save()
        send_task('azure', 'start')(vm.uuid.hex)

    def stop(self, vm):
        vm.schedule_stopping()
        vm.save()
        send_task('azure', 'stop')(vm.uuid.hex)

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
        options = self.settings.options or {}
        regex = re.compile(options.get('images_regex', r'.'))

        images = {}
        for image in self.manager.list_images():
            images.setdefault(image.name, [])
            images[image.name].append(image)

        cur_images = {i.backend_id: i for i in models.Image.objects.all()}
        for backend_images in images.values():
            backend_image = sorted(backend_images)[-1]  # get last image with same name (perhaps newest one)
            if not regex.match(backend_image.name):
                continue
            cur_images.pop(backend_image.id, None)
            try:
                models.Image.objects.update_or_create(
                    backend_id=backend_image.id,
                    defaults={
                        'name': backend_image.name,
                    })
            except IntegrityError:
                logger.warning(
                    'Could not create Azure image with id %s due to concurrent update',
                    backend_image.id)

        map(lambda i: i.delete(), cur_images.values())

    def push_link(self, service_project_link):
        # define cloud service name
        options = service_project_link.service.settings.options
        if options and 'cloud_service_name' in options:
            cloud_service_name = options['cloud_service_name']
            service_project_link.cloud_service_name = cloud_service_name
            service_project_link.save(update_fields=['cloud_service_name'])
        else:
            cloud_service_name = 'nc-%x' % service_project_link.project.uuid.node

        # create cloud
        services = [s.service_name for s in self.manager.ex_list_cloud_services()]
        if cloud_service_name not in services:
            logger.debug('About to create new azure cloud service for SPL %s', service_project_link.pk)
            self.manager.ex_create_cloud_service(cloud_service_name, self.location)
            service_project_link.cloud_service_name = cloud_service_name
            service_project_link.save(update_fields=['cloud_service_name'])
            logger.info('Successfully created new azure cloud for SPL %s', service_project_link.pk)
        else:
            logger.debug('Skipped azure cloud service creation for SPL %s - such cloud already exists', service_project_link.pk)

        # create storage
        storage_name = self.get_storage_name(cloud_service_name)
        storages = [s.service_name for s in self.manager.ex_list_storage_services()]
        if storage_name not in storages:
            logger.debug('About to create new azure storage for SPL %s', service_project_link.pk)
            self.manager.ex_create_storage_service(storage_name, self.location)

            # XXX: missed libcloud feature
            #      it will block celery worker for a while (5 min max)
            #      but it's easiest workaround for azure and general syncing workflow
            for _ in range(100):
                storage = self.get_storage(storage_name)
                if storage.storage_service_properties.status == 'Created':  # ResolvingDns otherwise
                    break
                time.sleep(30)
            logger.info('Successfully created new azure cloud for SPL %s', service_project_link.pk)
        else:
            logger.debug(
                'Skipped azure storage creation for SPL %s - such cloud already exists', service_project_link.pk)

    def reboot_vm(self, vm):
        self.manager.reboot_node(
            self.get_vm(vm.backend_id),
            ex_cloud_service_name=self.cloud_service_name,
            ex_deployment_slot=self.deployment)

    def stop_vm(self, vm):
        deployment_name = self.manager._get_deployment(
            service_name=self.cloud_service_name,
            deployment_slot=self.deployment
        ).name

        try:
            response = self.manager._perform_post(
                self.manager._get_deployment_path_using_name(
                    self.cloud_service_name, deployment_name
                ) + '/roleinstances/' + azure._str(vm.backend_id) + '/Operations',
                azure.AzureXmlSerializer.shutdown_role_operation_to_xml()
            )

            self.manager.raise_for_response(response, 202)
            self.manager._ex_complete_async_azure_operation(response)
        except Exception as e:
            six.reraise(AzureBackendError, e)

    def start_vm(self, vm):
        deployment_name = self.manager._get_deployment(
            service_name=self.cloud_service_name,
            deployment_slot=self.deployment
        ).name

        try:
            response = self.manager._perform_post(
                self.manager._get_deployment_path_using_name(
                    self.cloud_service_name, deployment_name
                ) + '/roleinstances/' + azure._str(vm.backend_id) + '/Operations',
                azure.AzureXmlSerializer.start_role_operation_to_xml()
            )

            self.manager.raise_for_response(response, 202)
            self.manager._ex_complete_async_azure_operation(response)
        except Exception as e:
            six.reraise(AzureBackendError, e)

    def destroy_vm(self, vm):
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
                ex_storage_service_name=self.get_storage_name(),
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
            six.reraise(AzureBackendError, e.message or "Virtual machine doesn't exist")

    def get_size(self, size_id):
        try:
            return next(s for s in self.manager.list_sizes() if s.id == size_id)
        except (StopIteration, LibcloudError) as e:
            six.reraise(AzureBackendError, e)

    def get_image(self, image_id):
        try:
            return next(s for s in self.manager.list_images() if s.id == image_id)
        except (StopIteration, LibcloudError) as e:
            six.reraise(AzureBackendError, e.message or "Image doesn't exist")

    def get_storage(self, storage_name):
        try:
            return next(s for s in self.manager.ex_list_storage_services() if s.service_name == storage_name)
        except (StopIteration, LibcloudError) as e:
            six.reraise(AzureBackendError, e.message or "Storage doesn't exist")

    def get_storage_name(self, cloud_service_name=None):
        if not cloud_service_name:
            cloud_service_name = self.cloud_service_name
        # Storage account name must be between 3 and 24 characters in length
        # and use numbers and lower-case letters only
        return re.sub(r'[\W_-]+', '', cloud_service_name.lower())[:24]

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
