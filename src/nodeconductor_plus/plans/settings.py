""" Plans application settings """

from django.conf import settings

NODECONDUCTOR_PLUS = getattr(settings, 'NODECONDUCTOR_PLUS', {})

DEFAULT_PLAN = getattr(NODECONDUCTOR_PLUS, 'DEFAULT_PLAN', {
    'name': 'Default',
    'price': 9.99,
    'quotas': (('nc_user_count', 2), ('nc_project_count', 2), ('nc_resource_count', 4),)
})
