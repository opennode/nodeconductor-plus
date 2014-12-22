from django.conf.urls import patterns, url

from ncauth import views


urlpatterns = patterns(
    '',
    url(r'^auth/signup/$', views.SignupView.as_view(), name='ncauth_signup'),
    url(r'^auth/signin/$', views.SigninView.as_view(), name='ncauth_signin'),
)
