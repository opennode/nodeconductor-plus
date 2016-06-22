from django.conf.urls import patterns, url

from . import views


urlpatterns = patterns(
    '',
    url(r'^api/agreements/approve_cb/$', views.approve_cb, name='agreement_approve_cb'),
    url(r'^api/agreements/cancel_cb/$', views.cancel_cb, name='agreement_cancel_cb'),
)


def register_in(router):
    router.register(r'plans', views.PlanViewSet)
    router.register(r'agreements', views.AgreementViewSet)
