from nodeconductor.core.permissions import StaffPermissionLogic
from nodeconductor.structure import perms as structure_perms


PERMISSION_LOGICS = (
    ('aws.AWSService', structure_perms.service_permission_logic),
    ('aws.AWSServiceProjectLink', structure_perms.service_project_link_permission_logic),
    ('aws.Instance', structure_perms.resource_permission_logic),
    ('aws.Volume', structure_perms.resource_permission_logic),
    ('aws.Image', StaffPermissionLogic(any_permission=True)),
    ('aws.Region', StaffPermissionLogic(any_permission=True)),
)
