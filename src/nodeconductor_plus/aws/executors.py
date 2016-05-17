from nodeconductor.core import executors
from nodeconductor.core.tasks import BackendMethodTask


class VolumeCreateExecutor(executors.CreateExecutor):

    @classmethod
    def get_task_signature(cls, volume, serialized_volume, **kwargs):
        return BackendMethodTask().si(
            serialized_volume, 'create_volume', state_transition='begin_creating')
