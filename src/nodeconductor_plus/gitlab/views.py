from nodeconductor.core import exceptions as core_exceptions
from nodeconductor.structure import views as structure_views

from . import models, serializers


class GitLabServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.Service.objects.all()
    serializer_class = serializers.ServiceSerializer


class GitLabServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.ServiceProjectLink.objects.all()
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
        if resource.projects.count():
            raise core_exceptions.IncorrectStateException(
                "This group contains projects. Only empty group can be deleted.")

        # Resource must be online in order to schedule_delition transition success
        # Forcely switch it offline since it's irrelevant for this type of service
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
            wiki_enabled=serializer.validated_data.get('wiki_enabled', False),
            issues_enabled=serializer.validated_data.get('issues_enabled', False),
            snippets_enabled=serializer.validated_data.get('snippets_enabled', False),
            merge_requests_enabled=serializer.validated_data.get('merge_requests_enabled', False))

    def perform_destroy(self, resource):
        # Resource must be online in order to schedule_delition transition success
        # Forcely switch it offline since it's irrelevant for this type of service
        resource.state = resource.States.OFFLINE
        resource.save()
        super(ProjectViewSet, self).perform_destroy(resource)
