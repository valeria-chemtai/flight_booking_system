from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from flights.models import Flight
from flights.serializers import (
    FlightCreateSerializer,
    FlightSlimReadOnlySerializer,
    FlightEmployeeReadOnlySerializer,
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
