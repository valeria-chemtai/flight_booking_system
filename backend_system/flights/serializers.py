from django.db import transaction

from rest_framework import serializers

from flights.models import Location, Flight, Seat


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')


class FlightSerializer(serializers.ModelSerializer):
    origin = LocationSerializer(required=False, allow_null=True)
    origin = LocationSerializer(required=False, allow_null=True)

    class Meta:
        model = Flight
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    @transaction.atomic
    def create(self, validated_data):
        origin_data = validated_data.pop('origin', None)
        if origin_data:
            origin_serializer = LocationSerializer(data=origin_data)
            origin_serializer.is_valid()
            origin_object = origin_serializer.save()

        destination_data = validated_data.pop('origin', None)
        if destination_data:
            destination_serializer = LocationSerializer(data=destination_data)
            destination_serializer.is_valid()
            destination_object = destination_serializer.save()

        flight = Flight.objects.create(
            origin=origin_object,
            destination=destination_object,
            **validated_data
        )
        flight.save()
        return flight

    @transaction.atomic
    def update(self, instance, validated_data):
        origin_data = validated_data.pop('origin', None)
        if origin_data:
            origin_serializer = LocationSerializer(instance.origin, data=origin_data)
            origin_serializer.is_valid()
            instance.origin = origin_serializer.save()

        destination_data = validated_data.pop('origin', None)
        if destination_data:
            destination_serializer = LocationSerializer(
                instance.destination, data=destination_data)
            destination_serializer.is_valid()
            instance.destination = destination_serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class SeatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Seat
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
