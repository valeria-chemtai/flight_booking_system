from rest_framework import viewsets

from bookings.models import Booking
from bookings.serializers import BookingCreateSerializer, BookingViewSerializer

from permissions import IsAuthenticatedUser


class BookingViewset(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    permission_classes = (IsAuthenticatedUser,)
    serializer_class = BookingCreateSerializer

    def get_queryset(self):
        if not self.request.user.is_staff:
            return super().get_queryset().filter(booked_by=self.request.user)
        else:
            return super().get_queryset()

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return BookingCreateSerializer
        return BookingViewSerializer
# method to get bookings for a particular flight
