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
