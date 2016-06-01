import logging
import sys

from celery import Task as CeleryTask
from django.utils import six

from nodeconductor.core import utils
from nodeconductor.core.tasks import BackendMethodTask, Task

from . import backend, handlers, log


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
            handlers.open_token_scope_alert(droplet.service_project_link)
            six.reraise(*sys.exc_info())
        else:
            handlers.close_token_scope_alert(droplet.service_project_link)
            return result
