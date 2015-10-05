import re

from rest_framework import serializers

from nodeconductor.core.fields import MappedChoiceField
from nodeconductor.structure import SupportedServices, serializers as structure_serializers, models as structure_models

from . import ResourceType, models
from .backend import GitLabBackendError


class ServiceSerializer(structure_serializers.BaseServiceSerializer):

    SERVICE_TYPE = SupportedServices.Types.GitLab
    SERVICE_ACCOUNT_FIELDS = {
        'backend_url': 'Host (e.g. http://git.example.com/)',
        'username': '',
        'password': '',
        'token': 'Used instead of username/password if supplied',
    }

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.GitLabService
        view_name = 'gitlab-detail'

    def get_fields(self):
        fields = super(ServiceSerializer, self).get_fields()
        fields['token'].label = 'Private token'
        fields['username'].label = 'Username or email'
        return fields


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):

    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.GitLabServiceProjectLink
        view_name = 'gitlab-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'gitlab-detail'},
        }


class BasicProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta(object):
        model = models.Project
        view_name = 'gitlab-project-detail'
        fields = ('url', 'uuid', 'name', 'web_url')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
        }


class GroupSerializer(structure_serializers.BaseResourceSerializer):

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='gitlab-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='gitlab-spl-detail',
        queryset=models.GitLabServiceProjectLink.objects.all(),
        write_only=True)

    projects = BasicProjectSerializer(many=True, read_only=True)

    path = serializers.CharField(max_length=100, write_only=True)

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.Group
        view_name = 'gitlab-group-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'path', 'web_url', 'projects'
        )

    def validate(self, attrs):
        if not re.match(r'[a-zA-Z0-9_.\s-]+', attrs['name']):
            raise serializers.ValidationError(
                {'name': "Name can contain only letters, digits, '_', '.', dash and space."})

        if not re.match(r'[a-zA-Z0-9_.\s-]+', attrs['path']):
            raise serializers.ValidationError(
                {'path': "Path can contain only letters, digits, '_', '.', dash and space."})

        if attrs['path'].startswith('-') or attrs['path'].endswith('.'):
            raise serializers.ValidationError(
                {'path': "Path cannot start with '-' or end in '.'."})

        return attrs


class ProjectSerializer(structure_serializers.BaseResourceSerializer):

    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='gitlab-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='gitlab-spl-detail',
        queryset=models.GitLabServiceProjectLink.objects.all(),
        write_only=True)

    group = serializers.HyperlinkedRelatedField(
        view_name='gitlab-group-detail',
        queryset=models.Group.objects.all(),
        lookup_field='uuid',
        required=False,
        write_only=True)

    wiki_enabled = serializers.BooleanField(write_only=True, required=False)
    issues_enabled = serializers.BooleanField(write_only=True, required=False)
    snippets_enabled = serializers.BooleanField(write_only=True, required=False)
    merge_requests_enabled = serializers.BooleanField(write_only=True, required=False)

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.Project
        view_name = 'gitlab-project-detail'
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'group', 'web_url', 'http_url_to_repo', 'ssh_url_to_repo', 'visibility_level',
            'wiki_enabled', 'issues_enabled', 'snippets_enabled', 'merge_requests_enabled'
        )
        read_only_fields = structure_serializers.BaseResourceSerializer.Meta.read_only_fields + (
            'web_url', 'http_url_to_repo', 'ssh_url_to_repo',
        )

    def get_fields(self):
        fields = super(ProjectSerializer, self).get_fields()
        if self.context['request'].method == 'GET':
            fields['visibility_level'] = MappedChoiceField(
                choices=[(v, k) for k, v in models.Project.Levels.CHOICES],
                choice_mappings={v: k for k, v in models.Project.Levels.CHOICES},
                read_only=True)

        return fields

    def validate(self, attrs):
        if not re.match(r'[a-zA-Z0-9_.\s-]+', attrs['name']):
            raise serializers.ValidationError(
                {'name': "Name can contain only letters, digits, '_', '-' and '.'."})

        if attrs['name'].startswith('-') or attrs['name'].endswith('.'):
            raise serializers.ValidationError(
                {'name': "Name cannot start with '-' or end in '.'."})

        if 'group' in attrs and attrs['group'].service_project_link != attrs['service_project_link']:
            raise serializers.ValidationError(
                {'group': "Group belongs to different service project link."})

        return attrs


class GroupImportSerializer(structure_serializers.BaseResourceImportSerializer):

    type = serializers.ChoiceField(choices=ResourceType.CHOICES, write_only=True)

    class Meta(structure_serializers.BaseResourceImportSerializer.Meta):
        model = models.Group
        view_name = 'gitlab-group-detail'
        fields = structure_serializers.BaseResourceImportSerializer.Meta.fields + ('type',)

    def create(self, validated_data):
        backend = self.context['service'].get_backend()
        try:
            group = backend.get_group(validated_data['backend_id'])
        except GitLabBackendError:
            raise serializers.ValidationError(
                {'backend_id': "Can't find group with ID %s" % validated_data['backend_id']})

        validated_data['name'] = group.name
        validated_data['path'] = group.path
        validated_data['state'] = structure_models.Resource.States.ONLINE
        del validated_data['type']

        return super(GroupImportSerializer, self).create(validated_data)


class ProjectImportSerializer(structure_serializers.BaseResourceImportSerializer):

    type = serializers.ChoiceField(choices=ResourceType.CHOICES, write_only=True)

    class Meta(structure_serializers.BaseResourceImportSerializer.Meta):
        model = models.Project
        view_name = 'gitlab-project-detail'
        fields = structure_serializers.BaseResourceImportSerializer.Meta.fields + ('type',)

    def create(self, validated_data):
        backend = self.context['service'].get_backend()
        try:
            project = backend.get_project(validated_data['backend_id'])
        except GitLabBackendError:
            raise serializers.ValidationError(
                {'backend_id': "Can't find project with ID %s" % validated_data['backend_id']})

        try:
            group_id = project.namespace.id
            group = models.Group.objects.get(backend_id=group_id)
        except models.Group.DoesNotExist:
            raise serializers.ValidationError(
                "You must import group with ID %s first" % group_id)

        validated_data['name'] = project.name
        validated_data['group'] = group
        validated_data['web_url'] = project.web_url
        validated_data['ssh_url_to_repo'] = project.ssh_url_to_repo
        validated_data['http_url_to_repo'] = project.http_url_to_repo
        validated_data['visibility_level'] = project.visibility_level
        validated_data['state'] = structure_models.Resource.States.ONLINE
        del validated_data['type']

        return super(ProjectImportSerializer, self).create(validated_data)
