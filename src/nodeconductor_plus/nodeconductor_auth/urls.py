from django.conf.urls import patterns, url

import views


urlpatterns = patterns(
    '',
    url(r'^google/$', views.GoogleView.as_view(), name='auth_google'),
    url(r'^facebook/$', views.FacebookView.as_view(), name='auth_facebook')
)
