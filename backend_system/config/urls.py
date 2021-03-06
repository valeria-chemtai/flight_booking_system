from django.contrib import admin
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static


API_VERSION = 1

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^django-rq/', include('django_rq.urls')),
    url(r'^v{}/auth/'.format(API_VERSION), include(('authentication.urls', 'authentication'), namespace='authentication')),
    url(r'^v{}/'.format(API_VERSION), include(('flights.urls', 'flights'), namespace='flights')),
    url(r'^v{}/'.format(API_VERSION), include(('bookings.urls', 'bookings'), namespace='bookings')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
