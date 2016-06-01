from nodeconductor.core.permissions import StaffPermissionLogic
from nodeconductor.structure import perms as structure_perms


PERMISSION_LOGICS = (
    ('digitalocean.DigitalOceanService', structure_perms.service_permission_logic),
    ('digitalocean.DigitalOceanServiceProjectLink', structure_perms.service_project_link_permission_logic),
    ('digitalocean.Droplet', structure_perms.resource_permission_logic),
    ('digitalocean.Image', StaffPermissionLogic(any_permission=True)),
    ('digitalocean.Region', StaffPermissionLogic(any_permission=True)),
    ('digitalocean.Size', StaffPermissionLogic(any_permission=True)),
)
