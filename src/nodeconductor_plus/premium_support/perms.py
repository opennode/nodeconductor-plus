from __future__ import unicode_literals

from nodeconductor.core.permissions import StaffPermissionLogic
from nodeconductor.structure import models as structure_models


PERMISSION_LOGICS = (
    ('premium_support.Plan', StaffPermissionLogic(any_permission=True)),
    ('premium_support.Worklog', StaffPermissionLogic(any_permission=True)),
)
