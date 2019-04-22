from django.conf.urls import url

from flights import views


urlpatterns = [
    url(r'^flights/$', views.FlightViewSet.as_view(
        actions={'post': 'create'}), name='flight-list'),
    url(r'^allowed-destinations/$', views.LocationViewSet.as_view(
        actions={'post': 'create'}), name='destination-list'),
    url(r'^flights/(?P<flight_pk>[0-9]+)/seats/$', views.SeatViewset.as_view(
        actions={'post': 'create'}), name='flight-seat-list'),
]
