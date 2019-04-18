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
        country = attrs.get('country').title()
        city = attrs.get('city').title()
        airport = attrs.get('airport').title()
        try:
            # check if such a location already exists
            # raise an exception if it exists
            Location.objects.get(country=country, city=city, airport=airport)
            raise serializers.ValidationError(
                'Location already exists, kindly use existing location.')
        except Location.DoesNotExist:
            # continue with action if location does not exist.
            pass
        return attrs


class LocationSlimSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        exclude = ('id', 'created_at', 'updated_at')
        read_only_fields = ('airport', 'city', 'country')


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


class FlightSerializer(serializers.ModelSerializer):
    origin = LocationSlimSerializer(read_only=True)
    destination = LocationSlimSerializer(read_only=True)
    departure_time = serializers.DateTimeField(allow_null=True, default=None)
    arrival_time = serializers.DateTimeField(required=False, default=None)

    class Meta:
        model = Flight
        fields = ('id', 'name', 'origin', 'destination', 'departure_time', 'arrival_time',
                  'gate')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_internal_value(self, data):
        internal_value = super(FlightSerializer, self).to_internal_value(data)
        internal_value['origin'] = data.get('origin')
        internal_value['destination'] = data.get('destination')
        return internal_value

    def validate(self, attrs):
        origin_data = attrs.get('origin')
        destination_data = attrs.get('destination')
        name = attrs.get('name').upper()
        departure_time = attrs.get('departure_time')
        try:
            if name and not departure_time:
                # if flight with given name exists but its not scheduled,
                # raise exception
                Flight.objects.get(name=name)
                raise serializers.ValidationError(
                    'Flight with same name exists, schedule existing flight.')
            if name and departure_time:
                # inform user if flight with given name exists and departure time has been set
                Flight.objects.get(name=name, departure_time=departure_time)
                raise serializers.ValidationError(
                    'Flight with same name is already scheduled for a trip at same departure time.')
        except Flight.DoesNotExist:
                # continue with action if flight does not exist.
                pass

        if (origin_data and destination_data):
            try:
                # check if origin and destination already exists
                # raise an exception if it doesn't
                origin_obj = Location.objects.get(
                    country=origin_data.get('country').title(),
                    city=origin_data.get('city').title(),
                    airport=origin_data.get('airport').title()
                )
                destination_obj = Location.objects.get(
                    country=destination_data.get('country').title(),
                    city=destination_data.get('city').title(),
                    airport=destination_data.get('airport').title()
                )
                if (origin_obj == destination_obj):
                    raise serializers.ValidationError(
                        'Flight origin and destination can not be the same.')
            except Location.DoesNotExist:
                raise serializers.ValidationError(
                    'Origin/destination given is not in the allowed destinations.')
        # pass objects to validated_data
        attrs['origin'] = origin_obj
        attrs['destination'] = destination_obj
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
            Seat.objects.get(flight=flight, row=row, letter=letter.upper())
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
