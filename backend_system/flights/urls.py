from django.conf.urls import url

from flights import views


urlpatterns = [
    url(r'^flights/$', views.FlightViewSet.as_view(
        actions={'post': 'create', 'get': 'list'}), name='flight-list'),
    url(r'^flights/(?P<pk>[a-f0-9-]+)/$', views.FlightViewSet.as_view(
        actions={'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='flight-detail'),
    url(r'^allowed-destinations/$', views.LocationViewSet.as_view(
        actions={'post': 'create', 'get': 'list'}), name='destination-list'),
    url(r'^allowed-destinations/(?P<pk>[a-f0-9-]+)/$', views.LocationViewSet.as_view(
        actions={'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
        name='destination-detail'),
    url(r'^flights/(?P<flight_pk>[a-f0-9-]+)/seats/$', views.SeatViewset.as_view(
        actions={'post': 'create', 'get': 'list'}), name='flight-seat-list'),
    url(r'^flights/(?P<flight_pk>[a-f0-9-]+)/seats/(?P<pk>[a-f0-9-]+)/$',
        views.SeatViewset.as_view(
            actions={'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
        name='flight-seat-detail'),
]
