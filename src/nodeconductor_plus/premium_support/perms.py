from __future__ import unicode_literals

from nodeconductor.core.permissions import StaffPermissionLogic, FilteredCollaboratorsPermissionLogic
from nodeconductor.structure import models as structure_models


PERMISSION_LOGICS = (
    ('premium_support.Plan', StaffPermissionLogic(any_permission=True)),
    ('premium_support.Worklog', StaffPermissionLogic(any_permission=True)),
    ('premium_support.Contract', FilteredCollaboratorsPermissionLogic(
        collaborators_query='project__customer__roles__permission_group__user',
        collaborators_filter={
            'project__customer__roles__role_type': structure_models.CustomerRole.OWNER,
        },
        any_permission=True,
    )),
    ('premium_support.SupportCase', FilteredCollaboratorsPermissionLogic(
        collaborators_query='contract__project__customer__roles__permission_group__user',
        collaborators_filter={
            'contract__project__customer__roles__role_type': structure_models.CustomerRole.OWNER,
        },
        any_permission=True,
    )),
)
