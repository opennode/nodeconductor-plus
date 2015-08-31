from nodeconductor.core.permissions import FilteredCollaboratorsPermissionLogic, StaffPermissionLogic
from nodeconductor.structure import models as structure_models, perms as structure_perms


PERMISSION_LOGICS = (
    ('digitalocean.DigitalOceanService', FilteredCollaboratorsPermissionLogic(
        collaborators_query='customer__roles__permission_group__user',
        collaborators_filter={
            'customer__roles__role_type': structure_models.CustomerRole.OWNER,
        },
        any_permission=True,
    )),
    ('digitalocean.DigitalOceanServiceProjectLink', FilteredCollaboratorsPermissionLogic(
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
    ('digitalocean.Droplet', structure_perms.resource_permission_logic),
    ('digitalocean.Image', StaffPermissionLogic(any_permission=True)),
    ('digitalocean.Region', StaffPermissionLogic(any_permission=True)),
    ('digitalocean.Size', StaffPermissionLogic(any_permission=True)),
)
