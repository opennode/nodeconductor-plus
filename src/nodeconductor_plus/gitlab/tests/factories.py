import factory

from django.core.urlresolvers import reverse

from nodeconductor.structure.tests import factories as structure_factories

from .. import models


class GitLabServiceFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.GitLabService

    name = factory.Sequence(lambda n: 'service%s' % n)
    settings = factory.SubFactory(structure_factories.ServiceSettingsFactory)
    customer = factory.SubFactory(structure_factories.CustomerFactory)

    @classmethod
    def get_url(self, service=None):
        if service is None:
            service = GitLabServiceFactory()
        return 'http://testserver' + reverse('gitlab-detail', kwargs={'uuid': service.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('gitlab-list')


class GitLabServiceProjectLinkFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.GitLabServiceProjectLink

    service = factory.SubFactory(GitLabServiceFactory)
    project = factory.SubFactory(structure_factories.ProjectFactory)


class BaseGitLabResourceFactory(factory.DjangoModelFactory):
    service_project_link = factory.SubFactory(GitLabServiceProjectLinkFactory)
    state = models.Project.States.ONLINE


class GitLabProjectFactory(BaseGitLabResourceFactory):
    class Meta(object):
        model = models.Project

    name = factory.Sequence(lambda n: 'project%s' % n)
    visibility_level = models.Project.Levels.PRIVATE

    @classmethod
    def get_url(self, project=None):
        if project is None:
            project = GitLabProjectFactory()
        return 'http://testserver' + reverse('gitlab-project-detail', kwargs={'uuid': project.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('gitlab-project-list')


class GitLabGroupFactory(BaseGitLabResourceFactory):
    class Meta(object):
        model = models.Group

    name = factory.Sequence(lambda n: 'group%s' % n)

    @classmethod
    def get_url(self, group=None):
        if group is None:
            group = GitLabGroupFactory()
        return 'http://testserver' + reverse('gitlab-group-detail', kwargs={'uuid': group.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('gitlab-group-list')

