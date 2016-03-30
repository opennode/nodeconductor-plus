import functools
import sys

from celery import shared_task, chain
from django.utils import six, timezone

from nodeconductor.core.tasks import save_error_message, transition, retry_if_false
from nodeconductor_plus.digitalocean.backend import TokenScopeError

from . import handlers
from .models import Droplet


def save_token_scope(func):
    """
    Open alert if token scope is read-only.
    Close alert if token scope if read-write.
    It should be applied to droplet provisioning tasks.
    """
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except TokenScopeError:
            droplet = kwargs['transition_entity']
            handlers.open_token_scope_alert(droplet.service_project_link)
            six.reraise(*sys.exc_info())
        else:
            droplet = kwargs['transition_entity']
            handlers.close_token_scope_alert(droplet.service_project_link)
            return result
    return wrapped


@shared_task(name='nodeconductor.digitalocean.provision')
def provision(droplet_uuid, **kwargs):
    chain(
        provision_droplet.si(droplet_uuid, **kwargs),
        wait_for_action_complete.s(droplet_uuid),
    ).apply_async(
        link=set_online.si(droplet_uuid),
        link_error=set_erred.si(droplet_uuid))


@shared_task(name='nodeconductor.digitalocean.destroy')
@transition(Droplet, 'begin_deleting')
@save_error_message
@save_token_scope
def destroy(droplet_uuid, transition_entity=None):
    droplet = transition_entity
    try:
        backend = droplet.get_backend()
        backend.destroy_droplet(droplet.backend_id)
    except:
        set_erred(droplet_uuid)
        raise
    else:
        droplet.delete()


@shared_task(name='nodeconductor.digitalocean.start')
def start(droplet_uuid):
    chain(
        begin_starting.s(droplet_uuid),
        wait_for_action_complete.s(droplet_uuid),
    ).apply_async(
        link=set_online.si(droplet_uuid),
        link_error=set_erred.si(droplet_uuid))


@shared_task(name='nodeconductor.digitalocean.stop')
def stop(droplet_uuid):
    chain(
        begin_stopping.s(droplet_uuid),
        wait_for_action_complete.s(droplet_uuid),
    ).apply_async(
        link=set_offline.si(droplet_uuid),
        link_error=set_erred.si(droplet_uuid))


@shared_task(name='nodeconductor.digitalocean.restart')
def restart(droplet_uuid):
    chain(
        begin_restarting.s(droplet_uuid),
        wait_for_action_complete.s(droplet_uuid),
    ).apply_async(
        link=set_online.si(droplet_uuid),
        link_error=set_erred.si(droplet_uuid))


@shared_task(max_retries=300, default_retry_delay=3)
@retry_if_false
def wait_for_action_complete(action_id, droplet_uuid):
    droplet = Droplet.objects.get(uuid=droplet_uuid)
    backend = droplet.get_backend()
    action = backend.manager.get_action(action_id)
    return action.status == 'completed'


@shared_task(is_heavy_task=True)
@transition(Droplet, 'begin_provisioning')
@save_error_message
@save_token_scope
def provision_droplet(droplet_uuid, transition_entity=None, **kwargs):
    droplet = transition_entity
    backend = droplet.get_backend()
    backend_droplet = backend.provision_droplet(droplet, **kwargs)
    return backend_droplet.action_ids[-1]


@shared_task
@transition(Droplet, 'begin_starting')
@save_error_message
@save_token_scope
def begin_starting(droplet_uuid, transition_entity=None):
    droplet = transition_entity
    backend = droplet.get_backend()
    return backend.start_droplet(droplet.backend_id)


@shared_task
@transition(Droplet, 'begin_stopping')
@save_error_message
@save_token_scope
def begin_stopping(droplet_uuid, transition_entity=None):
    droplet = transition_entity
    backend = droplet.get_backend()
    return backend.stop_droplet(droplet.backend_id)


@shared_task
@transition(Droplet, 'begin_restarting')
@save_error_message
@save_token_scope
def begin_restarting(droplet_uuid, transition_entity=None):
    droplet = transition_entity
    backend = droplet.get_backend()
    return backend.restart_droplet(droplet.backend_id)


@shared_task
@transition(Droplet, 'set_online')
def set_online(droplet_uuid, transition_entity=None):
    droplet = transition_entity
    droplet.start_time = timezone.now()

    backend = droplet.get_backend()
    backend_droplet = backend.get_droplet(droplet.backend_id)
    droplet.external_ips = backend_droplet.ip_address

    droplet.save(update_fields=['start_time', 'external_ips'])


@shared_task
@transition(Droplet, 'set_offline')
def set_offline(droplet_uuid, transition_entity=None):
    droplet = transition_entity
    droplet.start_time = None
    droplet.save(update_fields=['start_time'])


@shared_task
@transition(Droplet, 'set_erred')
def set_erred(droplet_uuid, transition_entity=None):
    pass
