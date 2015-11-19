import logging

from django.db import IntegrityError
from django.utils import six, dateparse
from libcloud.common.types import LibcloudError
from libcloud.compute.drivers.ec2 import EC2NodeDriver

from nodeconductor.core.utils import hours_in_month
from nodeconductor.structure import ServiceBackend, ServiceBackendError

from . import models


logger = logging.getLogger(__name__)


class AWSBackendError(ServiceBackendError):
    pass


class AWSBackend(object):

    def __init__(self, settings):
        backend_class = AWSDummyBackend if settings.dummy else AWSRealBackend
        self.backend = backend_class(settings)

    def __getattr__(self, name):
        return getattr(self.backend, name)


class AWSBaseBackend(ServiceBackend):

    def __init__(self, settings):
        region = 'us-east-1'
        if settings.options and 'region' in settings.options:
            region = settings.options['region']

        self.settings = settings
        self.manager = EC2NodeDriver(settings.username, settings.token, region=region)

    def sync(self):
        self.pull_service_properties()


class AWSRealBackend(AWSBaseBackend):
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

    def get_monthly_cost_estimate(self, instance):
        try:
            instance = (self.manager.list_nodes(ex_node_ids=[instance.backend_id]))[0]
        except Exception as e:
            six.reraise(AWSBackendError, e)

        size = next(s for s in self.manager.list_sizes() if s.id == instance.extra['instance_type'])

        # calculate a price for current month based on hourly rate
        return size.price * hours_in_month()

    def get_instance(self, instance_id):
        try:
            instance = (self.manager.list_nodes(ex_node_ids=[instance_id]))[0]
            volumes = {v.id: v.size for v in self.manager.list_volumes(instance)}
        except Exception as e:
            six.reraise(AWSBackendError, e)

        for device in instance.extra['block_device_mapping']:
            vid = device['ebs']['volume_id']
            if vid in volumes:
                device['ebs']['volume_size'] = volumes[vid]

        # libcloud is a funny buggy thing, put all required info here
        instance_type = next(s for s in self.manager.list_sizes() if s.id == instance.extra['instance_type'])

        return {
            'id': instance.id,
            'name': instance.name or instance.uuid,
            'cores': instance_type.extra.get('cpu', 1),
            'ram': instance_type.ram,
            'disk': self.gb2mb(sum(volumes.values())),
            'external_ips': instance.public_ips[0],
            'created': dateparse.parse_datetime(instance.extra['launch_time'])
        }

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

    def get_imported_resources(self):
        try:
            ids = [instance.id for instance in self.manager.list_nodes()]
            return models.Instance.objects.filter(backend_id__in=ids)
        except LibcloudError as e:
            return []


class AWSDummyBackend(AWSBaseBackend):
    pass
