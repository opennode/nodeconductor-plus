import logging
import calendar
import datetime

from django.utils import six
from libcloud.compute.drivers.ec2 import EC2NodeDriver
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
                models.Image.objects.update_or_create(
                    backend_id=backend_image.id,
                    defaults={
                        'name': backend_image.name,
                    })

        map(lambda i: i.delete(), cur_images.values())

    def get_cost_estimate(self, instance):
        try:
            instance = (self.manager.list_nodes(ex_node_ids=[instance.backend_id]))[0]
        except Exception as e:
            six.reraise(AWSBackendError, e)

        now = datetime.datetime.now()
        days = calendar.monthrange(now.year, now.month)[1]
        size = next(s for s in self.manager.list_sizes() if s.id == instance.extra['instance_type'])

        return 24 * days * size.price

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
        instance.size = {
            'disk': sum(volumes.values()),
            'ram': instance_type.ram,
            'cores': instance_type.extra.get('cpu', 0),
        }

        return instance

    def get_resources_for_import(self):
        cur_instances = models.Instance.objects.all().values_list('backend_id', flat=True)
        return [{
            'id': instance.id,
            'name': instance.name or instance.uuid,
            'created_at': instance.extra['launch_time'],
            'size': instance.extra['instance_type'],
        } for instance in self.manager.list_nodes()
            if instance.id not in cur_instances and
            instance.state == self.manager.NODE_STATE_MAP['running']]


class AWSDummyBackend(AWSBaseBackend):
    pass
