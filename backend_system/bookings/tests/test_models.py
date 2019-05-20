from django.test import TestCase

from authentication.models import User
from bookings.models import Booking
from flights.models import Location, Flight, Seat


class FlightTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='flightsystem@email.com', password='flightpassword')
        self.location1 = Location.objects.create(
            country='Kenya',
            city='Nairobi',
            airport='JKIA'
        )
        self.location2 = Location.objects.create(
            country='France',
            city='PAris',
            airport='Plane de Paris'
        )
        self.flight = Flight.objects.create(
            name='FLIGHT1',
            gate='G20',
            created_by=self.user
        )
        self.seat = Seat.objects.create(letter='A', row='1', flight=self.flight)
        self.booking = Booking.objects.create(
            origin=self.location1,
            destination=self.location2,
            booked_by=self.user,
            flight=self.flight,
            seat=self.seat
        )

    def test_booking_created_successfully(self):
        self.assertEqual(Booking.objects.all().count(), 1)

    def test_delete_soft_deletes(self):
        self.assertIsNone(self.booking.deleted_at)
        self.booking.delete()
        self.assertEqual(Booking.objects.all().count(), 0)
        self.assertEqual(Booking.objects_with_deleted.all().count(), 1)
        self.assertIsNotNone(Booking.objects_with_deleted.get(pk=self.booking.pk).deleted_at)
