from rest_framework.exceptions import NotFound
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from flights.models import Flight, Location, Seat
from flights.serializers import (
    FlightCreateSerializer,
    FlightSlimReadOnlySerializer,
    FlightEmployeeReadOnlySerializer,
    FlightSeatsViewSerializer,
    LocationSerializer,
    SeatSerializer,
)
from flights.permissions import FlightsPermissions


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    permission_classes = (FlightsPermissions,)

    def get_queryset(self):
        return super().get_queryset()

    def get_serializer_class(self):
        if self.action == 'list':
            if self.request.user.is_staff:
                return FlightEmployeeReadOnlySerializer
            else:
                return FlightSlimReadOnlySerializer
        return FlightCreateSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (FlightsPermissions,)

    def get_queryset(self):
        return super().get_queryset()


class SeatViewset(viewsets.ModelViewSet):
    queryset = Seat.objects.all()
    permission_classes = (FlightsPermissions,)

    def get_serializer_class(self):
        """Get serializer class"""
        if self.action == 'list':
            return FlightSeatsViewSerializer
        return SeatSerializer

    def get_queryset(self):
        # filter seats by flight
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

    def create(self, request, *args, **kwargs):
        # allow users to create a bunch of seats at ago
        # the user provides a list of seat letters and list of row numbers.
        rows = self.request.query_params.getlist('row', None)
        letters = self.request.query_params.getlist('letter', None)
        if rows and letters:
            # iterate through the lists provided to create seats.
            data = {}
            data['flight'] = request.data.get('flight')
            data['class_group'] = request.data.get('class_group', 'Economy')
            for letter in letters:
                for row in rows:
                    data['row'] = row
                    data['letter'] = letter
                    serializer = self.get_serializer(data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
            message = {'message': 'Seats created successfully.'}
            return Response(data=message, status=status.HTTP_201_CREATED)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)
