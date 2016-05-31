from celery import chain

from nodeconductor.core import executors
from nodeconductor.core.tasks import StateTransitionTask
from nodeconductor.core.models import RuntimeStateMixin

from . import tasks


class DropletCreateExecutor(executors.CreateExecutor):

    @classmethod
    def get_task_signature(cls, droplet, serialized_droplet, **kwargs):
        return chain(
            tasks.SafeBackendMethodTask(is_heavy_task=True).si(
                serialized_droplet, 'provision',
                state_transition='begin_creating',
                runtime_state='provisioning',
                success_runtime_state=RuntimeStateMixin.RuntimeStates.ONLINE,
                **kwargs),
            tasks.WaitForActionComplete().s(serialized_droplet).set(countdown=30))


class DropletDeleteExecutor(executors.DeleteExecutor):

    @classmethod
    def get_task_signature(cls, droplet, serialized_droplet, **kwargs):
        if droplet.backend_id:
            return tasks.SafeBackendMethodTask().si(
                serialized_droplet, 'destroy', state_transition='begin_deleting')
        else:
            return StateTransitionTask().si(serialized_droplet, state_transition='begin_deleting')


class DropletStateChangeExecutor(executors.UpdateExecutor):

    @classmethod
    def get_task_signature(cls, droplet, serialized_droplet, method=None, final_state=None, **kwargs):
        return chain(
            tasks.SafeBackendMethodTask().si(
                serialized_droplet, method,
                state_transition='begin_updating',
                success_runtime_state=final_state),
            tasks.WaitForActionComplete().s(serialized_droplet).set(countdown=10))


class DropletResizeExecutor(executors.UpdateExecutor):

    @classmethod
    def get_task_signature(cls, droplet, serialized_droplet, backend_size_id=None, disk=None, **kwargs):
        return chain(
            tasks.SafeBackendMethodTask().si(
                serialized_droplet, 'resize',
                state_transition='begin_updating',
                runtime_state='resizing',
                success_runtime_state=RuntimeStateMixin.RuntimeStates.ONLINE,
                backend_size_id=backend_size_id,
                disk=disk),
            tasks.WaitForActionComplete().s(serialized_droplet).set(countdown=10),
            tasks.LogDropletResized().si(serialized_droplet))
