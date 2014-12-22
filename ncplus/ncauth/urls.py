from django.conf.urls import patterns, url

from ncauth import views


urlpatterns = patterns(
    '',
    url(r'^auth/signup/$', views.SignupView.as_view(), name='auth_signup'),
)
9