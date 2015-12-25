import collections
import hashlib
import logging

from django.db import IntegrityError
from django.utils import six, dateparse
from libcloud.common.types import LibcloudError
from libcloud.compute.drivers.ec2 import EC2NodeDriver, INSTANCE_TYPES
from libcloud.compute.types import NodeState

from nodeconductor.core.models import SshPublicKey
from nodeconductor.core.tasks import send_task
from nodeconductor.core.utils import hours_in_month
from nodeconductor.structure import ServiceBackend, ServiceBackendError

from . import models

logger = logging.getLogger(__name__)


class SizeQueryset(object):
    def __init__(self):
        self.items = []
        for val in INSTANCE_TYPES.values():
            self.items.append(SizeQueryset.Size(uuid=hashlib.sha1(val['id']).hexdigest(),
                                                pk=val['id'],
                                                name=val['name'],
                                                cores=isinstance(val.get('cores'), int) and val['cores'] or 1,
                                                ram=val['ram'],
                                                disk=ServiceBackend.gb2mb(val['disk']),
                                                price=float(val.get('price', 0))))

        self.items = list(sorted(self.items, key=lambda s: (s.cores, s.ram)))

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


class ExtendedEC2NodeDriver(EC2NodeDriver):
    def ex_terminate_node(self, node):
        """
        Terminate the node

        :param      node: Node which should be used
        :type       node: :class:`Node`

        :rtype: ``bool``
        """
        params = {'Action': 'TerminateInstances'}
        params.update(self._pathlist('InstanceId', [node.id]))
        res = self.connection.request(self.path, params=params).object
        return self._get_state_boolean(res)

    def ex_reboot_node(self, node):
        """
        Reboot the node

        :param      node: Node which should be used
        :type       node: :class:`Node`

        :rtype: ``bool``
        """
        params = {'Action': 'RebootInstances'}
        params.update(self._pathlist('InstanceId', [node.id]))
        res = self.connection.request(self.path, params=params).object
        return self._get_state_boolean(res)


class AWSBackendError(ServiceBackendError):
    pass


class AWSBaseBackend(ServiceBackend):
    State = NodeState

    def __init__(self, settings):
        super(AWSBaseBackend, self).__init__(settings)
        self.settings = settings

    # Lazy init
    @property
    def manager(self):
        if not hasattr(self, '_manager'):
            region = 'us-east-1'
            if self.settings.options and 'region' in self.settings.options:
                region = self.settings.options['region']

            self._manager = ExtendedEC2NodeDriver(
                self.settings.username, self.settings.token, region=region)
        return self._manager

    def sync(self):
        self.pull_service_properties()

    def provision(self, vm, image=None, size=None, ssh_key=None):
        vm.ram = size.ram
        vm.disk = size.disk
        vm.cores = size.cores
        vm.save()

        send_task('aws', 'provision')(
                vm.uuid.hex,
                backend_image_id=image.backend_id,
                backend_size_id=size.pk,
                ssh_key_uuid=ssh_key.uuid.hex if ssh_key else None)

    def destroy(self, vm, force=False):
        if force:
            vm.delete()
            return

        vm.schedule_deletion()
        vm.save()
        send_task('aws', 'destroy')(vm.uuid.hex)

    def start(self, vm):
        vm.schedule_starting()
        vm.save()
        send_task('aws', 'start')(vm.uuid.hex)

    def stop(self, vm):
        vm.schedule_stopping()
        vm.save()
        send_task('aws', 'stop')(vm.uuid.hex)

    def restart(self, vm):
        vm.schedule_restarting()
        vm.save()
        send_task('aws', 'restart')(vm.uuid.hex)


class AWSBackend(AWSBaseBackend):
    """ NodeConductor interface to AWS EC2 API.
        https://libcloud.apache.org/
    """

    def ping(self):
        try:
            self.manager.list_images(ex_owner='self')
        except:
            return False
        else:
            return True

    def ping_resource(self, instance):
        try:
            self.manager.list_nodes(ex_node_ids=[instance.backend_id])
        except:
            return False
        else:
            return True

    def pull_service_properties(self):
        self.pull_images()

    def pull_images(self):
        cur_images = {i.backend_id: i for i in models.Image.objects.all()}
        for backend_image in self.manager.list_images(ex_owner='amazon'):
            cur_images.pop(backend_image.id, None)
            if backend_image.name:
                try:
                    models.Image.objects.update_or_create(
                        backend_id=backend_image.id,
                        defaults={
                            'name': backend_image.name,
                        })
                except IntegrityError:
                    logger.warning(
                        'Could not create AWS image with id %s due to concurrent update',
                        backend_image.id)

        map(lambda i: i.delete(), cur_images.values())

    def provision_vm(self, vm, backend_image_id=None, backend_size_id=None, ssh_key_uuid=None):
        if ssh_key_uuid:
            ssh_key = SshPublicKey.objects.get(uuid=ssh_key_uuid)
            try:
                backend_ssh_key = self.get_or_create_ssh_key(ssh_key)
            except LibcloudError as e:
                logger.exception('Unable to provision SSH key %s', ssh_key_uuid)
                six.reraise(AWSBackendError, e)

        try:
            backend_vm = self.manager.create_node(
                    name=vm.name,
                    image=self.get_image(backend_image_id),
                    size=self.get_size(backend_size_id),
                    ex_keyname=backend_ssh_key['keyName'],
                    ex_custom_data=vm.user_data)
        except LibcloudError as e:
            logger.exception('Failed to provision virtual machine %s', vm.name)
            six.reraise(AWSBackendError, e)

        if ssh_key_uuid:
            vm.key_name = ssh_key.name
            vm.key_fingerprint = ssh_key.fingerprint

        vm.backend_id = backend_vm.id
        vm.save()
        return vm

    def reboot_vm(self, vm):
        try:
            self.manager.ex_reboot_node(self.get_vm(vm.backend_id))
        except Exception as e:
            logger.exception('Unable to reboot Amazon virtual machine %s', vm.uuid.hex)
            six.reraise(AWSBackendError, six.text_type(e))

    def stop_vm(self, vm):
        try:
            self.manager.ex_stop_node(self.get_vm(vm.backend_id))
            logger.exception('Unable to stop Amazon virtual machine %s', vm.uuid.hex)
        except Exception as e:
            six.reraise(AWSBackendError, six.text_type(e))

    def start_vm(self, vm):
        try:
            self.manager.ex_start_node(self.get_vm(vm.backend_id))
            logger.exception('Unable to start Amazon virtual machine %s', vm.uuid.hex)
        except Exception as e:
            six.reraise(AWSBackendError, six.text_type(e))

    def destroy_vm(self, vm):
        try:
            self.manager.ex_terminate_node(self.get_vm(vm.backend_id))
            logger.exception('Unable to destroy Amazon virtual machine %s', vm.uuid.hex)
        except Exception as e:
            six.reraise(AWSBackendError, six.text_type(e))

    def get_monthly_cost_estimate(self, instance):
        try:
            instance = (self.manager.list_nodes(ex_node_ids=[instance.backend_id]))[0]
        except Exception as e:
            six.reraise(AWSBackendError, e)

        size = self.get_size(instance.extra['instance_type'])

        # calculate a price for current month based on hourly rate
        return size.price * hours_in_month()

    def get_instance(self, instance_id):
        try:
            instance = self.get_vm(instance_id)
            volumes = {v.id: v.size for v in self.manager.list_volumes(instance)}
        except Exception as e:
            six.reraise(AWSBackendError, e)

        for device in instance.extra['block_device_mapping']:
            vid = device['ebs']['volume_id']
            if vid in volumes:
                device['ebs']['volume_size'] = volumes[vid]

        # libcloud is a funny buggy thing, put all required info here
        instance_type = self.get_size(instance.extra['instance_type'])

        return {
            'id': instance.id,
            'name': instance.name or instance.uuid,
            'cores': instance_type.extra.get('cpu', 1),
            'ram': instance_type.ram,
            'disk': self.gb2mb(sum(volumes.values())),
            'external_ips': instance.public_ips[0],
            'created': dateparse.parse_datetime(instance.extra['launch_time'])
        }

    def get_vm(self, vm_id):
        return self.manager.list_nodes(ex_node_ids=[vm_id])[0]

    def get_size(self, size_id):
        try:
            return next(s for s in self.manager.list_sizes() if s.id == size_id)
        except (StopIteration, LibcloudError) as e:
            logger.exception("Size %s doesn't exist", size_id)
            six.reraise(AWSBackendError, e)

    def get_image(self, image_id):
        try:
            return next(s for s in self.manager.list_images() if s.id == image_id)
        except (StopIteration, LibcloudError) as e:
            logger.exception("Image %s doesn't exist", image_id)
            six.reraise(AWSBackendError, e)

    def get_or_create_ssh_key(self, ssh_key):
        try:
            return self.pull_ssh_key(ssh_key)
        except LibcloudError:
            return self.push_ssh_key(ssh_key)

    def pull_ssh_key(self, ssh_key):
        return self.manager.ex_describe_keypair(ssh_key.name)

    def push_ssh_key(self, ssh_key):
        return self.manager.ex_import_keypair_from_string(ssh_key.name, ssh_key.public_key)

    def get_resources_for_import(self):
        try:
            instances = self.manager.list_nodes()
        except LibcloudError as e:
            six.reraise(AWSBackendError, e)
        cur_instances = models.Instance.objects.all().values_list('backend_id', flat=True)

        return [
            self.get_instance(instance.id)
            for instance in instances
            if instance.id not in cur_instances and
            instance.state == self.manager.NODE_STATE_MAP['running']
        ]

    def get_managed_resources(self):
        try:
            ids = [instance.id for instance in self.manager.list_nodes()]
            return models.Instance.objects.filter(backend_id__in=ids)
        except LibcloudError:
            return []
