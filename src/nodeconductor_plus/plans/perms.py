from __future__ import unicode_literals

from nodeconductor.core.permissions import StaffPermissionLogic


PERMISSION_LOGICS = (
    ('plans.Plan', StaffPermissionLogic(any_permission=True)),
    ('plans.PlanQuota', StaffPermissionLogic(any_permission=True)),
)
