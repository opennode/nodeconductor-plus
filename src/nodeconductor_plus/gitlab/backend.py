import gitlab
import logging

from django.utils import six
from django.contrib.auth import get_user_model

from nodeconductor.core.utils import pwgen
from nodeconductor.core.tasks import send_task
from nodeconductor.structure import ServiceBackend, ServiceBackendError

from .models import Group, Project


logger = logging.getLogger(__name__)


class GitLabBackendError(ServiceBackendError):
    pass


class GitLabBackend(object):

    def __init__(self, settings):
        backend_class = GitLabDummyBackend if settings.dummy else GitLabRealBackend
        self.backend = backend_class(settings)

    def __getattr__(self, name):
        return getattr(self.backend, name)


class GitLabBaseBackend(ServiceBackend):

    def __init__(self, settings):
        self.settings = settings

    def provision(self, resource, **kwargs):
        kwargs.update({'name': resource.name, 'description': resource.description})
        if isinstance(resource, Group):
            send_task('gitlab', 'provision_group')(resource.uuid.hex, **kwargs)
        elif isinstance(resource, Project):
            send_task('gitlab', 'provision_project')(resource.uuid.hex, **kwargs)
        else:
            raise NotImplementedError

    def destroy(self, resource):
        resource.schedule_deletion()
        resource.save()

        if isinstance(resource, Group):
            send_task('gitlab', 'destroy_group')(resource.uuid.hex)
        elif isinstance(resource, Project):
            send_task('gitlab', 'destroy_project')(resource.uuid.hex)
        else:
            raise NotImplementedError

    def add_user(self, user, service_project_link):
        try:
            for group in service_project_link.groups.all():
                self.add_group_member(group, user)
                logger.info("User %s added to Gitlab group %s", user.username, group.backend_url)

            for project in service_project_link.projects.all():
                self.add_project_member(project, user)
                logger.info("User %s added to Gitlab project %s", user.username, project.backend_url)

        except gitlab.GitlabError as e:
            six.reraise(GitLabBackendError, e)

    def remove_user(self, user, service_project_link):
        try:
            for group in service_project_link.groups.all():
                self.delete_group_member(group, user)
                logger.info("User %s removed from Gitlab group %s", user.username, group.backend_url)

            for project in service_project_link.projects.all():
                self.delete_project_member(project, user)
                logger.info("User %s removed from Gitlab project %s", user.username, project.backend_url)

        except gitlab.GitlabError as e:
            six.reraise(GitLabBackendError, e)

    def add_ssh_key(self, ssh_key, service_project_link=None):
        try:
            self.push_ssh_key(ssh_key)
        except gitlab.GitlabError as e:
            logger.exception('Failed to propagate ssh public key %s to backend', ssh_key.name)
            six.reraise(GitLabBackendError, e)

    def remove_ssh_key(self, ssh_key, service_project_link=None):
        try:
            self.delete_ssh_key(ssh_key)
        except gitlab.GitlabError as e:
            logger.exception('Failed to delete ssh public key %s from backend', ssh_key.name)
            six.reraise(GitLabBackendError, e)


class GitLabRealBackend(GitLabBaseBackend):
    """ NodeConductor interface to GitLab API.
        http://doc.gitlab.com/ce/api/README.html
        http://github.com/gpocentek/python-gitlab
    """

    class Namespace(gitlab.GitlabObject):
        _url = '/namespaces'

    def __init__(self, settings):
        self.settings = settings
        self.manager = gitlab.Gitlab(
            settings.backend_url,
            private_token=settings.token,
            email=settings.username,
            password=settings.password)

        try:
            self.manager.auth()
        except gitlab.GitlabAuthenticationError as e:
            six.reraise(GitLabBackendError, e)

    def provision_group(self, group, **kwargs):
        try:
            backend_group = self.manager.Group(kwargs)
            backend_group.save()
        except gitlab.GitlabCreateError as e:
            six.reraise(GitLabBackendError, e)

        group.backend_id = backend_group.id
        group.save()

        for user in self._get_project_users(group.service_project_link.project):
            self.add_group_member(group, user)

    def provision_project(self, project, **kwargs):
        if project.group:
            try:
                for namespace in self.Namespace.list(self.manager):
                    if namespace.kind == 'group' and namespace.path == project.group.path:
                        kwargs['namespace_id'] = namespace.id
            except gitlab.GitlabError as e:
                logger.exception(
                    "Cannot fetch namespaces list for Gitlab %s", self.settings.backend_url)

        try:
            backend_project = self.manager.Project(kwargs)
            backend_project.save()
        except gitlab.GitlabCreateError as e:
            six.reraise(GitLabBackendError, e)

        project.backend_id = backend_project.id
        project.web_url = backend_project.web_url
        project.ssh_url_to_repo = backend_project.ssh_url_to_repo
        project.http_url_to_repo = backend_project.http_url_to_repo
        project.save()

        for user in self._get_project_users(project.service_project_link.project):
            self.add_project_member(project, user)

    def delete_group(self, group):
        try:
            backend_group = self.manager.Group(group.backend_id)
            backend_group.delete()
        except gitlab.GitlabDeleteError as e:
            six.reraise(GitLabBackendError, e)

    def delete_project(self, project):
        try:
            backend_project = self.manager.Project(project.backend_id)
            backend_project.delete()
        except gitlab.GitlabDeleteError as e:
            six.reraise(GitLabBackendError, e)

    def _get_access_level(self, resource, user):
        project = resource.service_project_link.project

        ACCESS_MAPPING = {
            project.roles.model.ADMINISTRATOR: 40,  # MASTER
            project.roles.model.MANAGER: 30,        # DEVELOPER
        }

        if not hasattr(self, '_cached_roles'):
            self._cached_roles = {}

        if not self._cached_roles.get(user.username):
            try:
                role_type = next(r.role_type for r in project.roles.filter(permission_group__user=user))
            except StopIteration:
                raise GitLabBackendError(
                    "Cannot add user %s to Gitlab %s", user.username, self.settings.backend_url)
            else:
                self._cached_roles[user.username] = ACCESS_MAPPING[role_type]

        return self._cached_roles[user.username]

    def _get_project_users(self, project):
        return get_user_model().objects.filter(groups__projectrole__project=project)

    def add_group_member(self, group, user):
        backend_user = self.get_or_create_user(user)
        member = gitlab.GroupMember(
            self.manager,
            {
                'user_id': backend_user.id,
                'group_id': group.backend_id,
                'access_level': self._get_access_level(group, user),
            })
        member.save()

    def add_project_member(self, project, user):
        backend_user = self.get_or_create_user(user)
        member = gitlab.ProjectMember(
            self.manager,
            {
                'user_id': backend_user.id,
                'project_id': project.backend_id,
                'access_level': self._get_access_level(project, user),
            })
        member.save()

    def delete_group_member(self, group, user):
        backend_user = self.get_user(user)

        if not backend_user:
            logger.warn("Cannot remove user %s from Gitlab %s", user.username, self.settings.backend_url)
            return

        member = gitlab.GroupMember(
            self.manager,
            {
                'user_id': backend_user.id,
                'group_id': group.backend_id,
            })
        member._created = True
        member.delete()

    def delete_project_member(self, project, user):
        backend_user = self.get_user(user)

        if not backend_user:
            logger.warn("Cannot remove user %s from Gitlab %s", user.username, self.settings.backend_url)
            return

        member = gitlab.ProjectMember(
            self.manager,
            {
                'user_id': backend_user.id,
                'project_id': project.backend_id,
            })
        member._created = True
        member.delete()

    def push_ssh_key(self, ssh_key):
        backend_user = self.get_or_create_user(ssh_key.user)
        user_key = gitlab.UserKey(
            self.manager,
            {
                'user_id': backend_user.id,
                'title': ssh_key.name,
                'key': ssh_key.public_key,
            })
        user_key.save()

    def delete_ssh_key(self, ssh_key):
        backend_user = self.get_or_create_user(ssh_key.user)
        for user_key in gitlab.UserKey.list(self.manager, user_id=backend_user.id):
            if user_key.key == ssh_key.public_key:
                user_key.delete()
                break

    def get_user(self, user):
        if not hasattr(self, '_cached_users'):
            self._cached_users = {}

        try:
            return self._cached_users[user.username]
        except KeyError:
            for backend_user in self.manager.User(search=user.username):
                if backend_user.username == user.username:
                    self._cached_users[user.username] = backend_user
                    return backend_user

        return None

    def get_or_create_user(self, user):
        backend_user = self.get_user(user)
        if not backend_user:
            backend_user = self.manager.User({
                'email': user.email,
                'name': user.full_name,
                'username': user.username,
                'password': pwgen(),
                'extern_uid': user.uuid.hex,
            })
            backend_user.save()
            self._cached_users[user.username] = backend_user
        return backend_user


class GitLabDummyBackend(GitLabBaseBackend):
    pass
