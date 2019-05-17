from django.db import transaction

from rest_framework import serializers

from authentication.models import User
from authentication.serializers import BasicUserSerializer
from bookings.models import Booking
from bookings.emails import send_booking_email
from flights.models import Flight, Location, Seat
from flights.serializers import (
    FlightSerializer,
    FlightSeatsViewSerializer,
    LocationSlimSerializer,
    SeatSlimSerializer,
)


class BookingViewSerializer(serializers.ModelSerializer):
    booked_by = BasicUserSerializer(read_only=True)
    origin = serializers.SlugRelatedField(
        queryset=Location.objects.all(),
        many=False, slug_field='city', read_only=False)
    destination = serializers.SlugRelatedField(
        queryset=Location.objects.all(),
        many=False, slug_field='city', read_only=False)
    travel_date = serializers.DateField(allow_null=True, default=None)
    flight = FlightSerializer(read_only=True)
    seat = FlightSeatsViewSerializer(allow_null=True, default=None)

    class Meta:
        model = Booking
        fields = ('id', 'booked_by', 'origin', 'destination', 'travel_date',
                  'flight', 'seat', )
        read_only_fields = ('id', 'created_at', 'updated_at')


class BookingCreateSerializer(serializers.ModelSerializer):
    booked_by = BasicUserSerializer(read_only=True)
    origin = LocationSlimSerializer(read_only=True)
    destination = LocationSlimSerializer(read_only=True)
    travel_date = serializers.DateField(allow_null=True, default=None)
    flight = serializers.SlugRelatedField(
        queryset=Flight.objects.all(),
        many=False, slug_field='name', allow_null=True, required=False)
    seat = SeatSlimSerializer(allow_null=True, default=None)

    class Meta:
        model = Booking
        fields = ('id', 'booked_by', 'origin', 'destination', 'travel_date',
                  'flight', 'seat', )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_internal_value(self, data):
        internal_value = super(BookingCreateSerializer, self).to_internal_value(data)
        internal_value['origin'] = data.get('origin')
        internal_value['destination'] = data.get('destination')
        internal_value['seat'] = data.get('seat')
        return internal_value

    def validate(self, attrs):
        origin_data = attrs.get('origin')
        destination_data = attrs.get('destination')
        flight = attrs.get('flight')
        travel_date = attrs.get('travel_date')
        seat_data = attrs.get('seat')
        if origin_data:
            try:
                # check if origin and destination already exists
                # raise an exception if it doesn't
                origin_obj = Location.objects.get(
                    country=origin_data.get('country').title(),
                    city=origin_data.get('city').title(),
                    airport=origin_data.get('airport').title()
                )
                # pass origin object to validated_data
                attrs['origin'] = origin_obj
            except Location.DoesNotExist:
                raise serializers.ValidationError(
                    'Origin given is not in the allowed destinations.')

        if destination_data:
            try:
                destination_obj = Location.objects.get(
                    country=destination_data.get('country').title(),
                    city=destination_data.get('city').title(),
                    airport=destination_data.get('airport').title()
                )
                # pass destination object to validated_data
                attrs['destination'] = destination_obj
            except Location.DoesNotExist:
                raise serializers.ValidationError(
                    'Destination given is not in the allowed destinations.')

        # origin and destination should not be the same
        if (attrs['origin'] and attrs['destination']) and \
                (attrs['origin'] == attrs['destination']):
            raise serializers.ValidationError(
                'Origin and destination can not be the same.')
        # make sure users flight choice is okay
        viable_flights = Flight.objects.filter(
            origin=attrs.get('origin'), destination=attrs.get('destination'))
        if flight:
            if flight not in viable_flights:
                raise serializers.ValidationError(
                    'Invalid flight choosen for booking information; origin/destination, given.')
            if flight.departure_time and (flight.departure_time.date() != travel_date):
                raise serializers.ValidationError(
                    'Invalid flight choosen for booking information; travel_date, given.')
        # make sure users flight seat choice is valid
        if seat_data:
            try:
                seat_obj = Seat.objects.get(
                    flight=flight, row=seat_data.get('row'),
                    letter=seat_data.get('letter').upper())
                attrs['seat'] = seat_obj
            except Seat.objects.DoesNotExist:
                raise serializers.ValidationError(
                    'Invalid seat choice.')
        if attrs['seat']:
            if self.context['request']._request.method == 'POST':
                viable_seats = Seat.objects.filter(
                    flight=flight, class_group=attrs['seat'].class_group).exclude(booked=True)
                if attrs['seat'] not in viable_seats:
                    raise serializers.ValidationError(
                        'Invalid seat choice.')
            if self.context['request']._request.method == 'PUT':
                if self.instance.seat and (self.instance.seat != attrs['seat']):
                    viable_seats = Seat.objects.filter(
                        flight=flight, class_group=attrs['seat'].class_group).exclude(booked=True)
                    if attrs['seat'] not in viable_seats:
                        raise serializers.ValidationError('Invalid seat choice.')
                    # set initially booked seat to not booked
                    self.instance.seat.booked = False
                    self.instance.seat.save()
            # set seat to booked
            attrs['seat'].booked = True
            attrs['seat'].save()
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        booking = Booking.objects.create(
            booked_by=user,
            **validated_data
        )
        send_booking_email(booking)
        return booking

    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class FlightBookingsSerializer(serializers.ModelSerializer):
    booked_by = BasicUserSerializer(read_only=False)
    seat = FlightSeatsViewSerializer(allow_null=True, default=None)

    class Meta:
        model = Booking
        fields = ('id', 'booked_by', 'seat', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')

    def to_internal_value(self, data):
        internal_value = super(FlightBookingsSerializer, self).to_internal_value(data)
        internal_value['seat'] = data.get('seat')
        internal_value['booked_by'] = data.get('booked_by')
        return internal_value

    def validate(self, attrs):
        seat_data = attrs.get('seat')
        booked_by_data = attrs.get('booked_by')

        if booked_by_data:
            try:
                attrs['booked_by'] = User.objects.get(email=booked_by_data.get('email'))
            except User.objects.DoesNotExist:
                raise serializers.ValidationError('Make sure the user you are trying to book for'
                                                  ' is maintained in the system.')

        if seat_data:
            try:
                seat_obj = Seat.objects.get(
                    flight=self.context['flight'], row=seat_data.get('row'),
                    letter=seat_data.get('letter').upper())
                attrs['seat'] = seat_obj
            except Seat.objects.DoesNotExist:
                raise serializers.ValidationError(
                    'Invalid seat choice.')
        if attrs['seat']:
            if self.context['request']._request.method == 'POST':
                viable_seats = Seat.objects.filter(
                    flight=self.context['flight'],
                    class_group=attrs['seat'].class_group).exclude(booked=True)
                if attrs['seat'] not in viable_seats:
                    raise serializers.ValidationError(
                        'Invalid seat choice.')
            if self.context['request']._request.method == 'PUT':
                if self.instance.seat and (self.instance.seat != attrs['seat']):
                    viable_seats = Seat.objects.filter(
                        flight=self.context['flight'],
                        class_group=attrs['seat'].class_group).exclude(booked=True)
                    if attrs['seat'] not in viable_seats:
                        raise serializers.ValidationError('Invalid seat choice.')
                    # set initially booked seat to not booked
                    self.instance.seat.booked = False
                    self.instance.seat.save()
            # set seat to booked
            attrs['seat'].booked = True
            attrs['seat'].save()

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        flight = self.context['flight']
        booking = Booking.objects.create(
            flight=flight,
            origin=flight.origin,
            destination=flight.destination,
            **validated_data
        )
        send_booking_email(booking)
        return booking

    @transaction.atomic
    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
