import gitlab
import logging
import dateutil

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import six, timezone
import reversion

from nodeconductor.core.tasks import send_task
from nodeconductor.core.utils import pwgen
from nodeconductor.structure import ServiceBackend, ServiceBackendError

from . import ResourceType
from .models import Group, Project


logger = logging.getLogger(__name__)
# XXX: monkey-patch GitLab API parameters for user creation.
# Should be removed after API version update
gitlab.User.optionalCreateAttrs.append('confirm')


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

    def ping(self):
        # Session validation occurs on class creation so assume it's active
        return True

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
            self.get_or_create_user(user)

            for group in service_project_link.groups.all():
                self.add_group_member(group, user)
                logger.info("User %s added to Gitlab group %s", user.username, group.uuid.hex)

            for project in service_project_link.projects.all():
                self.add_project_member(project, user)
                logger.info("User %s added to Gitlab project %s", user.username, project.uuid.hex)

        except gitlab.GitlabError as e:
            six.reraise(GitLabBackendError, e)

    def remove_user(self, user, service_project_link):
        try:
            for group in service_project_link.groups.all():
                self.delete_group_member(group, user)
                logger.info("User %s removed from Gitlab group %s", user.username, group.uuid.hex)

            for project in service_project_link.projects.all():
                self.delete_project_member(project, user)
                logger.info("User %s removed from Gitlab project %s", user.username, project.uuid.hex)

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

    def get_resources_for_import(self, resource_type=None):
        resources = []

        if resource_type is None or resource_type == ResourceType.PROJECT:
            cur_projects = Project.objects.all().values_list('backend_id', flat=True)
            cur_groups = Group.objects.all().values_list('backend_id', flat=True)
            for proj in self.get_gitlab_objects(gitlab.Project):
                # Only project from already imported groups are available for import
                if str(proj.id) not in cur_projects and str(proj.namespace.id) in cur_groups:
                    resources.append({
                        'id': proj.id,
                        'type': ResourceType.PROJECT,
                        'name': proj.path_with_namespace,
                        'created_at': proj.created_at,
                        'public': proj.public,
                    })

        if resource_type is None or resource_type == ResourceType.GROUP:
            cur_groups = Group.objects.all().values_list('backend_id', flat=True)
            for grp in self.get_gitlab_objects(gitlab.Group):
                if str(grp.id) not in cur_groups:
                    resources.append({
                        'id': grp.id,
                        'type': ResourceType.GROUP,
                        'name': grp.name,
                    })

        return resources

    def update_statistics(self):
        for project in Project.objects.all():
            try:
                self.update_project_statistics(project)
            except gitlab.GitlabError as e:
                logger.warning('Failed to update statistics for project %s. Exception: %s.', project.name, str(e))


class GitLabRealBackend(GitLabBaseBackend):
    """NodeConductor interface to GitLab API.

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

    def get_gitlab_objects(self, object_cls, **kwargs):
        """Get GitLab objects iterator.

        Iterator hides pagination process and allows to iterate through all available objects.
        """
        page = kwargs.pop('page', 0)
        page_size = kwargs.pop('page_size', 20)
        while True:
            objects = object_cls.list(self.manager, page=page, page_size=page_size, **kwargs)
            for obj in objects:
                yield obj
            if not objects or len(objects) < page_size:
                raise StopIteration
            page += 1

    def ping_resource(self, resource):
        if isinstance(resource, Group):
            try:
                self.manager.Group(resource.backend_id)
            except gitlab.GitlabGetError:
                return False
        elif isinstance(resource, Project):
            try:
                self.manager.Project(resource.backend_id)
            except gitlab.GitlabGetError:
                return False
        else:
            raise NotImplementedError

        return True

    def provision_group(self, group, **kwargs):
        try:
            backend_group = self.manager.Group(kwargs)
            backend_group.save()
        except gitlab.GitlabCreateError as e:
            six.reraise(GitLabBackendError, e)

        group.backend_id = backend_group.id
        group.save()

        for user in group.service_project_link.get_related_users():
            self.add_group_member(group, user)

    def provision_project(self, project, **kwargs):
        if project.group:
            try:
                for namespace in self.get_gitlab_objects(self.Namespace):
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
        project.visibility_level = backend_project.visibility_level
        project.save()

        for user in project.service_project_link.get_related_users():
            self.add_project_member(project, user)

    def get_group(self, group_id):
        try:
            return self.manager.Group(group_id)
        except gitlab.GitlabGetError as e:
            six.reraise(GitLabBackendError, e)

    def get_project(self, project_id):
        try:
            return self.manager.Project(project_id)
        except gitlab.GitlabGetError as e:
            six.reraise(GitLabBackendError, e)

    def delete_group(self, group):
        try:
            backend_group = self.get_group(group.backend_id)
            backend_group.delete()
        except gitlab.GitlabDeleteError as e:
            six.reraise(GitLabBackendError, e)

    def delete_project(self, project):
        try:
            backend_project = self.get_project(project.backend_id)
            backend_project.delete()
        except gitlab.GitlabDeleteError as e:
            six.reraise(GitLabBackendError, e)

    def _get_access_level(self, resource, user):
        project = resource.service_project_link.project

        if not hasattr(self, '_cached_roles'):
            self._cached_roles = {}

        if not self._cached_roles.get(user.username):
            if (project.customer.has_user(user, role_type=project.customer.roles.model.OWNER) or
                    project.has_user(user, role_type=project.roles.model.ADMINISTRATOR)):
                access_level = gitlab.Group.DEVELOPER_ACCESS
            else:
                raise GitLabBackendError(
                    "Cannot add user %s to Gitlab %s. User has no role.", user.username, self.settings.backend_url)

            self._cached_roles[user.username] = access_level

        return self._cached_roles[user.username]

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
        self._send_access_gained_email(user, group)

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
        self._send_access_gained_email(user, project)

    def delete_group_member(self, group, user):
        backend_user = self.get_user(user)

        if not backend_user:
            logger.warn("Cannot remove user %s from Gitlab %s. User does not exist at GitLab.",
                        user.username, self.settings.backend_url)
            return

        members = [member for member in gitlab.GroupMember.list(self.manager, group_id=group.backend_id)
                   if member.username == backend_user.username]

        for member in members:
            member.delete()

    def delete_project_member(self, project, user):
        backend_user = self.get_user(user)

        if not backend_user:
            logger.warn("Cannot remove user %s from Gitlab %s", user.username, self.settings.backend_url)
            return

        members = [member for member in gitlab.ProjectMember.list(self.manager, project_id=project.backend_id)
                   if member.username == backend_user.username]

        for member in members:
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
            password = pwgen()
            backend_user = self.manager.User({
                'email': user.email,
                'name': user.full_name or user.username,
                'username': user.username,
                'password': password,
                'confirm': 'false',
            })
            backend_user.save()

            self._send_registration_email(user, password)
            self._cached_users[user.username] = backend_user
        return backend_user, user.username, password

    def update_project_statistics(self, project):
        quota = project.quotas.get(name='commit_count')
        last_version = reversion.get_for_date(quota, timezone.now())
        last_update = last_version.revision.date_created
        commit_count = 0
        for commit in self.get_gitlab_objects(gitlab.ProjectCommit, project_id=project.backend_id):
            if dateutil.parser.parse(commit.created_at) > last_update:
                commit_count += 1
            else:
                break
        if commit_count:
            project.add_quota_usage('commit_count', commit_count)

    def _send_registration_email(self, user, password):
        context = {
            'user': user,
            'password': password,
            'gitlab_url': self.settings.backend_url,
        }

        subject = render_to_string('gitlab/registration_email/subject.txt', context)
        text_message = render_to_string('gitlab/registration_email/message.txt', context)
        html_message = render_to_string('gitlab/registration_email/message.html', context)

        send_mail(subject, text_message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)

    def _send_access_gained_email(self, user, backend_resource):
        context = {
            'user': user,
            'resource': backend_resource,
            'gitlab_url': self.settings.backend_url,
            'resource_type': backend_resource.__class__.__name__,
        }

        subject = render_to_string('gitlab/access_gained_email/subject.txt', context)
        text_message = render_to_string('gitlab/access_gained_email/message.txt', context)
        html_message = render_to_string('gitlab/access_gained_email/message.html', context)

        send_mail(subject, text_message, settings.DEFAULT_FROM_EMAIL, [user.email], html_message=html_message)


class GitLabDummyBackend(GitLabBaseBackend):
    pass
