from celery import chain

from nodeconductor.core import executors
from nodeconductor.core import tasks as core_tasks
from nodeconductor_plus.aws.tasks import PollRuntimeStateTask


class VolumeCreateExecutor(executors.CreateExecutor):

    @classmethod
    def get_task_signature(cls, volume, serialized_volume, **kwargs):
        return chain(
            core_tasks.BackendMethodTask().si(
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
            return core_tasks.BackendMethodTask().si(
                serialized_volume, 'delete_volume', state_transition='begin_deleting')
        else:
            return core_tasks.StateTransitionTask().si(serialized_volume, state_transition='begin_deleting')


class VolumeDetachExecutor(executors.ActionExecutor):

    @classmethod
    def get_task_signature(cls, volume, serialized_volume, **kwargs):
        return chain(
            core_tasks.BackendMethodTask().si(
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
        return chain(
            core_tasks.BackendMethodTask().si(
                serialized_volume, 'attach_volume', state_transition='begin_updating'),
            PollRuntimeStateTask().si(
                 serialized_volume,
                 backend_pull_method='pull_volume_runtime_state',
                 success_state='inuse',
                 erred_state='error',
            ).set(countdown=10)
        )


class InstanceCreateExecutor(executors.CreateExecutor):

    @classmethod
    def get_task_signature(cls, instance, serialized_instance, image=None, size=None, ssh_key=None):
        kwargs = {
            'backend_image_id': image.backend_id,
            'backend_size_id': size.backend_id,
        }
        if ssh_key is not None:
            kwargs['ssh_key_uuid'] = ssh_key.uuid.hex

        return chain(
            core_tasks.BackendMethodTask().si(
                serialized_instance,
                backend_method='provision_vm',
                state_transition='begin_provisioning',
                **kwargs),
            PollRuntimeStateTask().si(
                serialized_instance,
                backend_pull_method='pull_vm_runtime_state',
                success_state='running',
                erred_state='error'
            ),
            core_tasks.BackendMethodTask().si(
                serialized_instance,
                backend_method='import_vm_volumes'
            ),
        )

    @classmethod
    def get_success_signature(cls, instance, serialized_instance, **kwargs):
        # XXX: This method is overridden to support old-style states.
        return core_tasks.StateTransitionTask().si(serialized_instance, state_transition='set_online')


class InstanceResizeExecutor(executors.ActionExecutor):

    @classmethod
    def pre_apply(cls, instance, **kwargs):
        instance.schedule_resizing()
        instance.save(update_fields=['state'])

    @classmethod
    def get_task_signature(cls, instance, serialized_instance, **kwargs):
        size = kwargs.pop('size')
        return chain(
            core_tasks.BackendMethodTask().si(
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
        return core_tasks.StateTransitionTask().si(serialized_instance, state_transition='set_resized')
