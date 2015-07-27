from nodeconductor.core.permissions import FilteredCollaboratorsPermissionLogic, StaffPermissionLogic
from nodeconductor.structure import models as structure_models


PERMISSION_LOGICS = (
    ('aws.Service', FilteredCollaboratorsPermissionLogic(
        collaborators_query='customer__roles__permission_group__user',
        collaborators_filter={
            'customer__roles__role_type': structure_models.CustomerRole.OWNER,
        },
        any_permission=True,
    )),
    ('aws.ServiceProjectLink', FilteredCollaboratorsPermissionLogic(
        collaborators_query=[
            'service__customer__roles__permission_group__user',
            'project__project_groups__roles__permission_group__user',
        ],
        collaborators_filter=[
            {'service__customer__roles__role_type': structure_models.CustomerRole.OWNER},
            {'project__project_groups__roles__role_type': structure_models.ProjectGroupRole.MANAGER},
        ],

        any_permission=True,
    )),
    ('aws.Instance', FilteredCollaboratorsPermissionLogic(
        collaborators_query='service_project_link__project__roles__permission_group__user',
        collaborators_filter={
            'service_project_link__project__roles__role_type': structure_models.ProjectRole.ADMINISTRATOR,
        },

        any_permission=True,
    )),
    ('aws.Image', StaffPermissionLogic(any_permission=True)),
)
