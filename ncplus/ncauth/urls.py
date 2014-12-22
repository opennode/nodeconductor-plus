from django.conf.urls import patterns, url

from ncauth import views


urlpatterns = patterns(
    '',
    url(r'^signup/$', views.SignupView.as_view(), name='ncauth_signup'),
    url(r'^signin/$', views.SigninView.as_view(), name='ncauth_signin'),
)
