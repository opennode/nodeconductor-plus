from celery import shared_task

from nodeconductor.core.tasks import transition

from .models import Group, Project


@shared_task(name='nodeconductor.gitlab.provision_group')
def provision_group(group_uuid, **kwargs):
    begin_group_provisioning.apply_async(
        args=(group_uuid,),
        kwargs=kwargs,
        link=set_group_online.si(group_uuid),
        link_error=set_group_erred.si(group_uuid))


@shared_task(name='nodeconductor.gitlab.provision_project')
def provision_project(project_uuid, **kwargs):
    begin_project_provisioning.apply_async(
        args=(project_uuid,),
        kwargs=kwargs,
        link=set_project_online.si(project_uuid),
        link_error=set_project_erred.si(project_uuid))


@shared_task(name='nodeconductor.gitlab.destroy_group')
@transition(Group, 'begin_deleting')
def destroy_group(group_uuid, transition_entity=None):
    group = transition_entity
    try:
        backend = group.get_backend()
        backend.delete_group(group)
    except:
        set_group_erred(group_uuid)
        raise
    else:
        group.delete()


@shared_task(name='nodeconductor.gitlab.destroy_project')
@transition(Project, 'begin_deleting')
def destroy_project(project_uuid, transition_entity=None):
    project = transition_entity
    try:
        backend = project.get_backend()
        backend.delete_project(project)
    except:
        set_project_erred(project_uuid)
        raise
    else:
        project.delete()


@shared_task
@transition(Group, 'begin_provisioning')
def begin_group_provisioning(group_uuid, transition_entity=None, **kwargs):
    group = transition_entity
    backend = group.get_backend()
    backend.provision_group(group, **kwargs)


@shared_task
@transition(Project, 'begin_provisioning')
def begin_project_provisioning(project_uuid, transition_entity=None, **kwargs):
    project = transition_entity
    backend = project.get_backend()
    backend.provision_project(project, **kwargs)


@shared_task
@transition(Group, 'set_online')
def set_group_online(group_uuid, transition_entity=None):
    pass


@shared_task
@transition(Project, 'set_online')
def set_project_online(project_uuid, transition_entity=None):
    pass


@shared_task
@transition(Group, 'set_erred')
def set_group_erred(group_uuid, transition_entity=None):
    pass


@shared_task
@transition(Project, 'set_erred')
def set_project_erred(project_uuid, transition_entity=None):
    pass
