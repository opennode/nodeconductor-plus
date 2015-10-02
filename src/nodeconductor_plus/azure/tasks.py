from celery import shared_task, chain

from django.utils import timezone

from nodeconductor.core.tasks import transition, retry_if_false

from .models import VirtualMachine
from .backend import AzureBackendError


@shared_task(name='nodeconductor.azure.provision')
def provision(vm_uuid, **kwargs):
    chain(
        provision_vm.s(vm_uuid, **kwargs),
        wait_for_provision_end.si(vm_uuid),
    ).apply_async(
        link=set_online.si(vm_uuid),
        link_error=set_erred.si(vm_uuid))


@shared_task(name='nodeconductor.azure.destroy')
@transition(VirtualMachine, 'begin_deleting')
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


@shared_task(name='nodeconductor.azure.restart')
def restart(vm_uuid):
    chain(
        begin_restarting.s(vm_uuid),
        wait_for_vm_online.si(vm_uuid),
    ).apply_async(
        link=set_online.si(vm_uuid),
        link_error=set_erred.si(vm_uuid))


# XXX: azure instance turns online few times during provisioning
#      hence give it at least 10 min before first try
@shared_task(max_retries=4, default_retry_delay=600)
@retry_if_false
def wait_for_provision_end(vm_uuid):
    vm = VirtualMachine.objects.get(uuid=vm_uuid)
    try:
        backend = vm.get_backend()
        backend_vm = backend.get_vm(vm.backend_id)
    except AzureBackendError:
        return False
    return backend_vm.extra['power_state'] == 'Started'


@shared_task(max_retries=300, default_retry_delay=3)
@retry_if_false
def wait_for_vm_online(vm_uuid):
    vm = VirtualMachine.objects.get(uuid=vm_uuid)
    backend = vm.get_backend()
    backend_vm = backend.get_vm(vm.backend_id)
    return backend_vm.extra['power_state'] == 'Started'


@shared_task(is_heavy_task=True)
@transition(VirtualMachine, 'begin_provisioning')
def provision_vm(vm_uuid, transition_entity=None, **kwargs):
    vm = transition_entity
    backend = vm.get_backend()
    backend.provision_vm(vm, **kwargs)


@shared_task
@transition(VirtualMachine, 'begin_restarting')
def begin_restarting(vm_uuid, transition_entity=None):
    vm = transition_entity
    backend = vm.get_backend()
    backend.reboot(vm)


@shared_task
@transition(VirtualMachine, 'set_online')
def set_online(vm_uuid, transition_entity=None):
    vm = transition_entity
    vm.start_time = timezone.now()
    vm.save(update_fields=['start_time'])


@shared_task
@transition(VirtualMachine, 'set_offline')
def set_offline(vm_uuid, transition_entity=None):
    vm = transition_entity
    vm.start_time = None
    vm.save(update_fields=['start_time'])


@shared_task
@transition(VirtualMachine, 'set_erred')
def set_erred(vm_uuid, transition_entity=None):
    pass
