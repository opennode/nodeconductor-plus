# NodeConductor Plus application base settings that will be imported into Django settings

# applications enabled by default
NODECONDUCTOR_PLUS_APPS = (
    'nodeconductor_plus.aws',
    'nodeconductor_plus.azure',
    'nodeconductor_plus.digitalocean',
    'nodeconductor_plus.gitlab',
    'nodeconductor_plus.nodeconductor_auth',
    'nodeconductor_plus.plans',
    'nodeconductor_plus.premium_support',
)

# NodeConductor Plus specific settings
NODECONDUCTOR_PLUS = {
    'GOOGLE_SECRET': 'CHANGE_ME_TO_GOOGLE_SECRET',
    'FACEBOOK_SECRET': 'CHANGE_ME_TO_FACEBOOK_SECRET',
}

