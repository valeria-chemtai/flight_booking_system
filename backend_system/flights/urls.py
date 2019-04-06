from django.conf.urls import url

from flights import views


urlpatterns = [
    url(r'^flights/$', views.FlightViewSet.as_view(
        actions={'post': 'create', 'get': 'list'}), name='flights-list'),
    url(r'^flights/(?P<pk>[0-9]+)/$', views.FlightViewSet.as_view(
        actions={'get': 'retrieve', 'put': 'update'}), name='flight-detail'),
]
