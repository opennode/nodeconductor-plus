from django.conf.urls import patterns, url

import views


urlpatterns = patterns(
    '',
    url(r'^api-auth/google/$', views.GoogleView.as_view(), name='auth_google'),
    url(r'^api-auth/facebook/$', views.FacebookView.as_view(), name='auth_facebook')
)
