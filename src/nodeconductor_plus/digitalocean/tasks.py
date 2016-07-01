import logging
import sys

from celery import Task as CeleryTask
from django.utils import six

from nodeconductor.core import utils
from nodeconductor.core.tasks import BackendMethodTask, Task

from . import backend, log


logger = logging.getLogger(__name__)


class WaitForActionComplete(CeleryTask):
    max_retries = 300
    default_retry_delay = 5

    def run(self, action_id, serialized_droplet):
        droplet = utils.deserialize_instance(serialized_droplet)
        backend = droplet.get_backend()
        action = backend.manager.get_action(action_id)
        if action.status == 'completed':
            return True
        else:
            self.retry()


class LogDropletResized(Task):

    def execute(self, droplet, *args, **kwargs):
        logger.info('Successfully resized droplet %s', droplet.uuid.hex)
        log.event_logger.droplet_resize.info(
            'Droplet {droplet_name} has been resized.',
            event_type='droplet_resize_succeeded',
            event_context={'droplet': droplet, 'size': droplet.size}
        )


class SafeBackendMethodTask(BackendMethodTask):
    """
    Open alert if token scope is read-only.
    Close alert if token scope if read-write.
    It should be applied to droplet provisioning tasks.
    """

    def execute(self, droplet, *args, **kwargs):
        try:
            result = super(SafeBackendMethodTask, self).execute(droplet, *args, **kwargs)
        except backend.TokenScopeError:
            droplet.service_project_link.service.raise_readonly_token_alert(droplet.service_project_link)
            six.reraise(*sys.exc_info())
        else:
            droplet.service_project_link.service.close_readonly_token_alert(droplet.service_project_link)
            return result


class RemoveSshKeyTask(BackendMethodTask):
    """ Additionally receives service that defined ssh_key backend """

    def get_backend(self, ssh_key):
        return self.service.settings.get_backend()

    def execute(self, ssh_key, serialized_service, *args, **kwargs):
        self.service = utils.deserialize_instance(serialized_service)
        super(RemoveSshKeyTask, self).execute(ssh_key, 'remove_ssh_key')
