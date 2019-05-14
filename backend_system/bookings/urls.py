from django.conf.urls import url

from bookings import views


urlpatterns = [
    url(r'^bookings/$', views.BookingViewset.as_view(
        actions={'post': 'create', 'get': 'list'}), name='booking-list'),
    url(r'^bookings/(?P<pk>[0-9]+)/$', views.BookingViewset.as_view(
        actions={'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='booking-detail'),
]
