from django.db import transaction

from rest_framework import serializers

from authentication.serializers import BasicUserSerializer
from flights.models import Location, Flight, Seat


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        country = attrs.get('country')
        city = attrs.get('city')
        airport = attrs.get('airport')
        try:
            # check if such a location already exists
            # raise an exception if it exists
            Location.objects.get(
                country=country.capitalize(), city=city.capitalize(), airport=airport.capitalize())
            raise serializers.ValidationError(
                "Location already exists, kindly use existing location.")
        except Location.DoesNotExist:
            # continue with action if location does not exist.
            pass
        return attrs


class FlightSlimReadOnlySerializer(serializers.ModelSerializer):
    origin = LocationSerializer(read_only=True)
    destination = LocationSerializer(read_only=True)
    departure_time = serializers.DateTimeField(allow_null=True, required=False)
    arrival_time = serializers.DateTimeField(allow_null=True, required=False)

    class Meta:
        model = Flight
        fields = ('id', 'name', 'origin', 'destination', 'departure_time', 'arrival_time',
                  'gate')
        read_only_fields = ('id', 'created_at', 'updated_at')


class FlightEmployeeReadOnlySerializer(serializers.ModelSerializer):
    origin = LocationSerializer(read_only=True)
    destination = LocationSerializer(read_only=True)
    departure_time = serializers.DateTimeField(allow_null=True, required=False)
    arrival_time = serializers.DateTimeField(allow_null=True, required=False)
    created_by = BasicUserSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = ('id', 'name', 'origin', 'destination', 'departure_time', 'arrival_time',
                  'gate', 'created_by')
        read_only_fields = ('id', 'created_at', 'updated_at')


class FlightCreateSerializer(serializers.ModelSerializer):
    origin = serializers.SlugRelatedField(
        queryset=Location.objects.all(),
        many=False, slug_field='airport', allow_null=True, required=False
    )
    destination = serializers.SlugRelatedField(
        queryset=Location.objects.all(),
        many=False, slug_field='airport', allow_null=True, required=False
    )
    departure_time = serializers.DateTimeField(allow_null=True, required=False)
    arrival_time = serializers.DateTimeField(allow_null=True, required=False)

    class Meta:
        model = Flight
        fields = ('id', 'name', 'origin', 'destination', 'departure_time', 'arrival_time',
                  'gate')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        origin = attrs.get('origin')
        destination = attrs.get('destination')

        if (origin and destination) and (origin == destination):
            raise serializers.ValidationError("Flight origin and destination can not be the same.")

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        flight = Flight.objects.create(
            created_by=user,
            **validated_data
        )
        flight.save()
        return flight

    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class SeatSerializer(serializers.ModelSerializer):
    flight = serializers.SlugRelatedField(
        many=False, slug_field='name', read_only=True)

    class Meta:
        model = Seat
        fields = ('id', 'class_group', 'letter', 'row', 'booked', 'flight')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate(self, attrs):
        flight = self.context['flight']
        row = attrs.get('row')
        letter = attrs.get('letter')
        try:
            # check if seat had been created before
            # raise an exception if it exists
            Seat.objects.get(flight=flight, row=row, letter=letter)
            raise serializers.ValidationError("Seat already exists.")
        except Seat.DoesNotExist:
            # continue with action if seat does not exist.
            pass
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        flight = self.context['flight']
        seat = Seat.objects.create(
            flight=flight,
            **validated_data
        )
        return seat


class FlightSeatsViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = ('id', 'class_group', 'seat', 'booked')
        read_only_fields = ('id', 'created_at', 'updated_at')
