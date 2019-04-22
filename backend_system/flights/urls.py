from django.conf.urls import url

from flights import views


urlpatterns = [
    url(r'^flights/$', views.FlightViewSet.as_view(
        actions={'post': 'create', 'get': 'list'}), name='flight-list'),
    url(r'^flights/(?P<pk>[0-9]+)/$', views.FlightViewSet.as_view(
        actions={'get': 'retrieve'}), name='flight-detail'),
    url(r'^allowed-destinations/$', views.LocationViewSet.as_view(
        actions={'post': 'create', 'get': 'list'}), name='destination-list'),
    url(r'^allowed-destinations/(?P<pk>[0-9]+)/$', views.LocationViewSet.as_view(
        actions={'get': 'retrieve'}),
        name='destination-detail'),
    url(r'^flights/(?P<flight_pk>[0-9]+)/seats/$', views.SeatViewset.as_view(
        actions={'post': 'create', 'get': 'list'}), name='flight-seat-list'),
    url(r'^flights/(?P<flight_pk>[0-9]+)/seats/(?P<pk>[0-9]+)/$', views.SeatViewset.as_view(
        actions={'get': 'retrieve'}),
        name='flight-seat-detail'),
]
