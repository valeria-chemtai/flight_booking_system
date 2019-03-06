from django.db.utils import IntegrityError
from django.test import TestCase

from flights.models import Location, Flight, Seat


class LocationTestCase(TestCase):
    # TO DO: Create BaseTestCase
    def setUp(self):
        self.location = Location.objects.create(
            country='Kenya',
            city='Nairobi',
            airport='JKIA'
        )

    def test_location_created_successfully(self):
        self.assertEqual(Location.objects.all().count(), 1)

    def test_unique_together(self):
        with self.assertRaises(IntegrityError):
            Location.objects.create(
                country='Kenya',
                city='Nairobi',
                airport='JKIA'
            )


class FlightTestCase(TestCase):
    def setUp(self):
        self.flight = Flight.objects.create(
            name='FLIGHT1',
            gate='G20'
        )

    def test_flight_created_successfully(self):
        self.assertEqual(Flight.objects.all().count(), 1)

    def test_unique_name(self):
        with self.assertRaises(IntegrityError):
            Flight.objects.create(name='FLIGHT1', gate='G20')

    def test_delete_soft_deletes(self):
        self.assertIsNone(self.flight.deleted_at)
        Flight.objects.get(name='FLIGHT1').delete()
        self.assertEqual(Flight.objects.all().count(), 0)
        self.assertEqual(Flight.objects_with_deleted.all().count(), 1)
        self.assertIsNotNone(Flight.objects_with_deleted.get(pk=self.flight.pk).deleted_at)

    def test_delete_soft_deletes_seats(self):
        seat = Seat.objects.create(letter='A', row='1', flight=self.flight)
        self.assertEqual(Seat.objects.all().count(), 1)
        Flight.objects.get(name='FLIGHT1').delete()
        self.assertEqual(Seat.objects.all().count(), 0)
        self.assertIsNotNone(Seat.objects_with_deleted.get(pk=seat.pk).deleted_at)


class SeatTestCase(TestCase):
    def setUp(self):
        self.flight = Flight.objects.create(
            name='FLIGHT1',
            gate='G20'
        )

        self.seat = Seat.objects.create(letter='A', row='1', flight=self.flight)

    def test_seat_created_successfully(self):
        self.assertEqual(Seat.objects.all().count(), 1)

    def test_seat_can_not_be_created_without_flight(self):
        with self.assertRaises(IntegrityError):
            Seat.objects.create(letter='A', row='1')
