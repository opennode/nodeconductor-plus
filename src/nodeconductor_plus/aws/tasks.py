from celery import shared_task, chain

from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition, retry_if_false

from .models import Instance
from .backend import AWSBackendError


@shared_task(name='nodeconductor.aws.provision')
def provision(vm_uuid, **kwargs):
    chain(
        provision_vm.si(vm_uuid, **kwargs),
        wait_for_vm_state.si(vm_uuid, 'RUNNING'),
    ).apply_async(
        link=set_online.si(vm_uuid),
        link_error=set_erred.si(vm_uuid))


@shared_task(name='nodeconductor.aws.destroy')
@transition(Instance, 'begin_deleting')
@save_error_message
def destroy(vm_uuid, transition_entity=None):
    vm = transition_entity
    try:
        backend = vm.get_backend()
        backend.destroy_vm(vm)
    except:
        set_erred(vm_uuid)
        raise
    else:
        vm.delete()


@shared_task(name='nodeconductor.aws.start')
def start(vm_uuid):
    chain(
        begin_starting.s(vm_uuid),
        wait_for_vm_state.si(vm_uuid, 'RUNNING'),
    ).apply_async(
        link=set_online.si(vm_uuid),
        link_error=set_erred.si(vm_uuid))


@shared_task(name='nodeconductor.aws.stop')
def stop(vm_uuid):
    chain(
        begin_stopping.s(vm_uuid),
        wait_for_vm_state.si(vm_uuid, 'STOPPED'),
    ).apply_async(
        link=set_offline.si(vm_uuid),
        link_error=set_erred.si(vm_uuid))


@shared_task(name='nodeconductor.aws.restart')
def restart(vm_uuid):
    Instance.objects.get(uuid=vm_uuid)
    chain(
        begin_restarting.s(vm_uuid),
        wait_for_vm_state.si(vm_uuid, 'RUNNING'),
    ).apply_async(
        link=set_online.si(vm_uuid),
        link_error=set_erred.si(vm_uuid))


@shared_task(max_retries=300, default_retry_delay=3)
@retry_if_false
def wait_for_vm_state(vm_uuid, state=''):
    vm = Instance.objects.get(uuid=vm_uuid)
    try:
        backend = vm.get_backend()
        manager = backend.get_manager(vm)
        backend_vm = manager.get_node(vm.backend_id)
    except AWSBackendError:
        return False
    return backend_vm.state == backend.State.fromstring(state)


@shared_task(is_heavy_task=True)
@transition(Instance, 'begin_provisioning')
@save_error_message
def provision_vm(vm_uuid, transition_entity=None, **kwargs):
    vm = transition_entity
    backend = vm.get_backend()
    backend.provision_vm(vm, **kwargs)


@shared_task
@transition(Instance, 'begin_starting')
@save_error_message
def begin_starting(vm_uuid, transition_entity=None):
    vm = transition_entity
    backend = vm.get_backend()
    backend.start_vm(vm)


@shared_task
@transition(Instance, 'begin_stopping')
@save_error_message
def begin_stopping(vm_uuid, transition_entity=None):
    vm = transition_entity
    backend = vm.get_backend()
    backend.stop_vm(vm)


@shared_task
@transition(Instance, 'begin_restarting')
@save_error_message
def begin_restarting(vm_uuid, transition_entity=None):
    vm = transition_entity
    backend = vm.get_backend()
    backend.reboot_vm(vm)


@shared_task
@transition(Instance, 'set_online')
def set_online(vm_uuid, transition_entity=None):
    vm = transition_entity
    vm.start_time = timezone.now()

    backend = vm.get_backend()
    manager = backend.get_manager(vm)
    backend_vm = manager.get_node(vm.backend_id)
    vm.external_ips = backend_vm.public_ips[0]

    vm.save(update_fields=['start_time', 'external_ips'])


@shared_task
@transition(Instance, 'set_offline')
def set_offline(vm_uuid, transition_entity=None):
    vm = transition_entity
    vm.start_time = None
    vm.save(update_fields=['start_time'])


@shared_task
@transition(Instance, 'set_erred')
def set_erred(vm_uuid, transition_entity=None):
    pass
