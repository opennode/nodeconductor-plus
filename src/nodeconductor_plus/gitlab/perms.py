from nodeconductor.structure import perms as structure_perms


PERMISSION_LOGICS = (
    ('gitlab.GitLabService', structure_perms.service_permission_logic),
    ('gitlab.GitLabServiceProjectLink', structure_perms.service_project_link_permission_logic),
    ('gitlab.Project', structure_perms.resource_permission_logic),
    ('gitlab.Group', structure_perms.resource_permission_logic),
)
