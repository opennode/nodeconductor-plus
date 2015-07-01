from . import views


def register_in(router):
    router.register(r'gitlab', views.GitLabServiceViewSet, base_name='gitlab')
    router.register(r'gitlab-groups', views.GroupViewSet, base_name='gitlab-group')
    router.register(r'gitlab-projects', views.ProjectViewSet, base_name='gitlab-project')
    router.register(r'gitlab-service-project-link', views.GitLabServiceProjectLinkViewSet, base_name='gitlab-spl')
