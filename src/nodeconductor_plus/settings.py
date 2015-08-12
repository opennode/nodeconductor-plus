# NodeConductor Plus application base settings that will be imported into Django settings

from datetime import timedelta

# applications enabled by default
NODECONDUCTOR_PLUS_APPS = (
    'nodeconductor_plus.aws',
    'nodeconductor_plus.azure',
    'nodeconductor_plus.digitalocean',
    'nodeconductor_plus.gitlab',
    'nodeconductor_plus.insights',
    'nodeconductor_plus.nodeconductor_auth',
    'nodeconductor_plus.plans',
    'nodeconductor_plus.premium_support',
)

# NodeConductor Plus specific settings
NODECONDUCTOR_PLUS = {
    'GOOGLE_SECRET': 'CHANGE_ME_TO_GOOGLE_SECRET',
    'FACEBOOK_SECRET': 'CHANGE_ME_TO_FACEBOOK_SECRET',
    'CREATE_CUSTOMER_ON_USER_CREATION': False,
    'PROJECTED_COSTS_EXCESS': 20,
}

NODECONDUCTOR_PLUS_CELERYBEAT_SCHEDULE = {
    'check-services': {
        'task': 'nodeconductor.insights.check_services',
        'schedule': timedelta(minutes=60),
        'args': ()
    },
    'check-customers': {
        'task': 'nodeconductor.insights.check_customers',
        'schedule': timedelta(hours=24),
        'args': (),
    },
}
