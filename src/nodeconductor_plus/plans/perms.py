from __future__ import unicode_literals

from nodeconductor.core.permissions import StaffPermissionLogic, FilteredCollaboratorsPermissionLogic
from nodeconductor.structure import models as structure_models


PERMISSION_LOGICS = (
    ('plans.Plan', StaffPermissionLogic(any_permission=True)),
    ('plans.PlanQuota', StaffPermissionLogic(any_permission=True)),
    ('plans.Agreement', FilteredCollaboratorsPermissionLogic(
        collaborators_query='customer__roles__permission_group__user',
        collaborators_filter={
            'roles__role_type': structure_models.CustomerRole.OWNER,
        },
        any_permission=True,
    )),
)
