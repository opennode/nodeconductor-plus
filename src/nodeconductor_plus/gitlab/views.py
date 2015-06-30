from nodeconductor.structure import views as structure_views

from . import models, serializers


class GitLabServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.GitLabService.objects.all()
    serializer_class = serializers.ServiceSerializer


class GitLabServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.GitLabServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class GroupViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            path=serializer.validated_data['path'])

    def perform_destroy(self, resource):
        resource.state = resource.States.OFFLINE
        resource.save()
        super(GroupViewSet, self).perform_destroy(resource)


class ProjectViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer

    def perform_provision(self, serializer):
        resource = serializer.save()
        backend = resource.get_backend()
        backend.provision(
            resource,
            group=serializer.validated_data.get('group'),
            wiki_enabled=serializer.validated_data.get('wiki_enabled', False),
            issues_enabled=serializer.validated_data.get('issues_enabled', False),
            snippets_enabled=serializer.validated_data.get('snippets_enabled', False),
            merge_requests_enabled=serializer.validated_data.get('merge_requests_enabled', False))

    def perform_destroy(self, resource):
        resource.state = resource.States.OFFLINE
        resource.save()
        super(ProjectViewSet, self).perform_destroy(resource)
