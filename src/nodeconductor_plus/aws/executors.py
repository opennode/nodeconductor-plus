from celery import chain

from nodeconductor.core import executors
from nodeconductor.core import tasks
from nodeconductor_plus.aws.tasks import PollRuntimeStateTask


class VolumeCreateExecutor(executors.CreateExecutor):

    @classmethod
    def get_task_signature(cls, volume, serialized_volume, **kwargs):
        return chain(
            tasks.BackendMethodTask().si(
                serialized_volume, 'create_volume', state_transition='begin_creating'),
            PollRuntimeStateTask().si(
                 serialized_volume,
                 backend_pull_method='pull_volume_runtime_state',
                 success_state='available',
                 erred_state='error',
            ).set(countdown=30)
        )


class VolumeDeleteExecutor(executors.DeleteExecutor):

    @classmethod
    def get_task_signature(cls, volume, serialized_volume, **kwargs):
        if volume.backend_id:
            return tasks.BackendMethodTask().si(
                serialized_volume, 'delete_volume', state_transition='begin_deleting')
        else:
            return tasks.StateTransitionTask().si(serialized_volume, state_transition='begin_deleting')


class VolumeDetachExecutor(executors.ActionExecutor):

    @classmethod
    def get_task_signature(cls, volume, serialized_volume, **kwargs):
        return chain(
            tasks.BackendMethodTask().si(
                serialized_volume, 'detach_volume', state_transition='begin_updating'),
            PollRuntimeStateTask().si(
                 serialized_volume,
                 backend_pull_method='pull_volume_runtime_state',
                 success_state='available',
                 erred_state='error'
            ).set(countdown=10)
        )


class VolumeAttachExecutor(executors.ActionExecutor):

    @classmethod
    def get_task_signature(cls, volume, serialized_volume, **kwargs):
        device = kwargs.pop('device')
        return chain(
            tasks.BackendMethodTask().si(
                serialized_volume,
                backend_method='attach_volume',
                state_transition='begin_updating',
                device=device),
            PollRuntimeStateTask().si(
                 serialized_volume,
                 backend_pull_method='pull_volume_runtime_state',
                 success_state='inuse',
                 erred_state='error',
            ).set(countdown=10)
        )


class InstanceResizeExecutor(executors.ActionExecutor):

    @classmethod
    def pre_apply(cls, instance, **kwargs):
        instance.schedule_resizing()
        instance.save(update_fields=['state'])

    @classmethod
    def get_task_signature(cls, instance, serialized_instance, **kwargs):
        size = kwargs.pop('size')
        return chain(
            tasks.BackendMethodTask().si(
                serialized_instance,
                backend_method='resize_vm',
                state_transition='begin_resizing',
                size_id=size.backend_id
            ),
            PollRuntimeStateTask().si(
                serialized_instance,
                backend_pull_method='pull_vm_runtime_state',
                success_state='stopped',
                erred_state='error'
            ).set(countdown=30)
        )

    @classmethod
    def get_success_signature(cls, instance, serialized_instance, **kwargs):
        return tasks.StateTransitionTask().si(serialized_instance, state_transition='set_resized')
