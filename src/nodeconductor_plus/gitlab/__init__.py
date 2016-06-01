default_app_config = 'nodeconductor_plus.gitlab.apps.GitLabConfig'


class ResourceType:
    GROUP = 'group'
    PROJECT = 'project'

    CHOICES = (
        (GROUP, 'Group'),
        (PROJECT, 'Projects'),
    )
