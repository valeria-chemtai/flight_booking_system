from datetime import datetime

from rest_framework.exceptions import NotFound
from rest_framework.decorators import list_route
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from bookings.models import Booking
from bookings.serializers import (
    BookingCreateSerializer,
    BookingViewSerializer,
    FlightBookingsSerializer,
)
from common.permissions import IsAuthenticatedUser
from flights.models import Flight, Seat
from flights.permissions import FlightsPermissions


class BookingViewset(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    permission_classes = (IsAuthenticatedUser,)
    serializer_class = BookingCreateSerializer

    def get_queryset(self):
        travel_date = self.request.query_params.get('travel_date', None)
        if not self.request.user.is_staff:
            queryset = super().get_queryset().filter(booked_by=self.request.user)
        else:
            queryset = super().get_queryset()
        if travel_date:
            date = datetime.strptime(travel_date, '%Y-%m-%d')
            return queryset.filter(travel_date=date)
        return queryset

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return BookingCreateSerializer
        return BookingViewSerializer


class FlightBookingsViewset(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    permission_classes = (FlightsPermissions,)
    serializer_class = FlightBookingsSerializer

    def get_queryset(self):
        flight_pk = self.kwargs['flight_pk']
        try:
            flight = Flight.objects.get(id=flight_pk)
            return super().get_queryset().filter(flight=flight)
        except Flight.DoesNotExist:
            NotFound

    def get_serializer_context(self):
        """Serializer context."""
        context = super().get_serializer_context()
        flight = Flight.objects.get(id=self.kwargs['flight_pk'])
        context['flight'] = flight
        return context

    @list_route(methods=['POST'], permission_classes=[FlightsPermissions],
                url_path='assign-flight-to-bookings')
    def assign_flight_to_bookings(self, request, *args, **kwargs):
        flight = self.get_serializer_context()['flight']
        # get total number of seats available
        total_flight_seats = Seat.objects.filter(flight=flight, booked=False).count()
        # fetch users to assign depending on the number of seats available
        bookings = Booking.objects.filter(
            travel_date=flight.departure_time,
            origin=flight.origin,
            destination=flight.destination,
            flight=None).order_by('created_at')[:total_flight_seats]
        for booking in bookings:
            booking.flight = flight
            booking.save()
            # send user email notifying them to select seats
        message = {'message': 'Flight assigned to first bookings based on number of seats.'}
        return Response(data=message, status=status.HTTP_200_OK)
