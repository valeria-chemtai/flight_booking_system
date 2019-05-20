from django.conf.urls import url, include

from rest_framework.routers import SimpleRouter

from bookings import views

router = SimpleRouter()

router.register(r'flights/(?P<flight_pk>[a-f0-9-]+)/bookings', views.FlightBookingsViewset,
                base_name='flight-bookings')

urlpatterns = [
    url('^', include(router.urls)),
    url(r'^bookings/$', views.BookingViewset.as_view(
        actions={'post': 'create', 'get': 'list'}), name='booking-list'),
    url(r'^bookings/(?P<pk>[a-f0-9-]+)/$', views.BookingViewset.as_view(
        actions={'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='booking-detail'),
]
