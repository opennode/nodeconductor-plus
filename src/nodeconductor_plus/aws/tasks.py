from celery import shared_task, chain

from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition, retry_if_false, Task, ErrorStateTransitionTask

from .models import Instance, Volume
from .backend import AWSBackendError


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


class RuntimeStateException(Exception):
    pass


class PollRuntimeStateTask(Task):
    max_retries = 300
    default_retry_delay = 5

    def get_backend(self, instance):
        return instance.get_backend()

    def execute(self, instance, backend_pull_method, success_state, erred_state):
        backend = self.get_backend(instance)
        getattr(backend, backend_pull_method)(instance)
        instance.refresh_from_db()
        if instance.runtime_state not in (success_state, erred_state):
            self.retry()
        elif instance.runtime_state == erred_state:
            raise RuntimeStateException(
                'Instance %s (PK: %s) runtime state become erred: %s' % (instance, instance.pk, erred_state))


class SetInstanceErredTask(ErrorStateTransitionTask):
    """ Mark instance as erred and delete resources that were not created. """

    def execute(self, instance):
        super(SetInstanceErredTask, self).execute(instance)

        # delete volume if it were not created on backend,
        # mark as erred if creation was started, but not ended,
        volume = instance.volume_set.first()
        if volume.state == Volume.States.CREATION_SCHEDULED:
            volume.delete()
        elif volume.state == Volume.States.OK:
            pass
        else:
            volume.set_erred()
            volume.save(update_fields=['state'])
