from nodeconductor.core import exceptions as core_exceptions
from nodeconductor.structure import views as structure_views

from . import ResourceType, models, serializers


class GitLabServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.GitLabService.objects.all()
    serializer_class = serializers.ServiceSerializer
    import_serializer_class = serializers.GroupImportSerializer

    def get_import_context(self):
        return {'resource_type': self.request.query_params.get('resource_type')}

    def get_serializer_class(self):
        if self.request.method == 'POST':
            resource_type = self.request.data.get('type')
            if resource_type == ResourceType.GROUP:
                return serializers.GroupImportSerializer
            elif resource_type == ResourceType.PROJECT:
                return serializers.ProjectImportSerializer
        return super(GitLabServiceViewSet, self).get_serializer_class()


class GitLabServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.GitLabServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class BaseGitLabResourceViewSet(structure_views.BaseOnlineResourceViewSet):

    def check_destroy(self, resource):
        pass

    def perform_managed_resource_destroy(self, resource):
        self.check_destroy(resource)
        super(BaseGitLabResourceViewSet, self).perform_managed_resource_destroy(resource)


class GroupViewSet(BaseGitLabResourceViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            path=serializer.validated_data['path'])

    def check_destroy(self, resource):
        if resource.projects.count():
            raise core_exceptions.IncorrectStateException(
                "This group contains projects. Only empty group can be deleted.")


class ProjectViewSet(BaseGitLabResourceViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            wiki_enabled=serializer.validated_data.get('wiki_enabled', False),
            issues_enabled=serializer.validated_data.get('issues_enabled', False),
            snippets_enabled=serializer.validated_data.get('snippets_enabled', False),
            merge_requests_enabled=serializer.validated_data.get('merge_requests_enabled', False))
