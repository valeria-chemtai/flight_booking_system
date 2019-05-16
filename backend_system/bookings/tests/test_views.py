import datetime

from django.shortcuts import reverse

from rest_framework.test import APITestCase

from authentication.models import User
from bookings.models import Booking
from flights.models import Location, Flight, Seat


class LocationViewSetTestCase(APITestCase):
    """Test LocationViewset TestCase."""
    def setUp(self):
        self.normal_user = User.objects.create_user(
            email='normal@email.com', password='flightpassword')
        self.other_normal_user = User.objects.create_user(
            email='other.normal@email.com', password='flightpassword')
        self.staff_user = User.objects.create_user(
            email='staff@email.com', password='flightpassword')
        self.staff_user.is_staff = True
        self.staff_user.save()

        self.location1 = Location.objects.create(
            country='Kenya',
            city='Nairobi',
            airport='JKIA'
        )
        self.location2 = Location.objects.create(
            country='France',
            city='Paris',
            airport='Gaulle'
        )
        self.flight = Flight.objects.create(
            name='FLIGHT1',
            gate='G20',
            origin=self.location2,
            destination=self.location1,
            created_by=self.staff_user,
            departure_time=datetime.datetime(2019, 6, 30, 7, 30, 30)
        )
        self.seat1 = Seat.objects.create(letter='A', row='1', flight=self.flight)
        self.seat2 = Seat.objects.create(letter='B', row='1', flight=self.flight)
        self.data = {
            'origin': {
                'country': 'France',
                'city': 'Paris',
                'airport': 'Gaulle'
            },
            'destination': {
                'country': 'Kenya',
                'city': 'Nairobi',
                'airport': 'Jkia'
            },
            'flight': 'FLIGHT1',
            'travel_date': '2019-06-30'
        }

    def test_user_can_book_flight(self):
        """Test user can book flight."""
        self.url = reverse('bookings:booking-list')
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['booked_by']['email'], self.normal_user.email)
        booking = Booking.objects.get(id=response.data['id'])
        self.assertEqual(booking.booked_by, self.normal_user)
        self.assertEqual(booking.flight, self.flight)

    def test_user_can_make_booking_without_specifying_flight(self):
        """Test user can make reservation."""
        self.data.pop('flight')
        self.url = reverse('bookings:booking-list')
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['booked_by']['email'], self.normal_user.email)
        # confirm booking has no flight
        booking = Booking.objects.get(id=response.data['id'])
        self.assertIsNone(booking.flight)

    def test_user_cannot_book_flight_if_invalid_flight_choice_origin_or_destination(self):
        """Test user cannot book flight with by choosing flight whose origin or
        destination defers from user."""
        self.flight.origin = self.location1
        self.flight.destination = self.location2
        self.flight.save()
        self.url = reverse('bookings:booking-list')
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'Invalid flight choosen for booking information; origin/destination, given.',
            str(response.data))

    def test_user_cannot_book_flight_if_invalid_flight_choice_travel_date(self):
        """Test user cannot book flight with a flight that does not depart on users travel_date."""
        self.data['travel_date'] = '2019-06-10'
        self.url = reverse('bookings:booking-list')
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            'Invalid flight choosen for booking information; travel_date, given.',
            str(response.data))

    def test_view_all_bookings(self):
        """Test view all bookings"""
        self.url = reverse('bookings:booking-list')
        self.client.force_authenticate(user=self.normal_user)
        # create two bookings for self.normal_user
        response1 = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response1.status_code, 201)
        response2 = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response2.status_code, 201)
        # create booking for self.other_normal_user
        self.client.force_authenticate(self.other_normal_user)
        response3 = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response3.status_code, 201)

        self.client.force_authenticate(user=self.normal_user)
        with self.subTest('Test normal_user can only see her two bookings'):
            response4 = self.client.get(self.url)
            self.assertEqual(response4.status_code, 200)
            self.assertEqual(response4.data['total_count'], 2)

        self.client.force_authenticate(user=self.other_normal_user)
        with self.subTest('Test self.other_normal_user can only see her two bookings'):
            response4 = self.client.get(self.url)
            self.assertEqual(response4.status_code, 200)
            self.assertEqual(response4.data['total_count'], 1)

        self.client.force_authenticate(user=self.staff_user)
        with self.subTest('Test staff user can see all bookings'):
            response4 = self.client.get(self.url)
            self.assertEqual(response4.status_code, 200)
            self.assertEqual(response4.data['total_count'], 3)

    def test_retrieve_booking(self):
        """Test can retrieve booking."""
        self.url = reverse('bookings:booking-list')
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 201)
        detail_url = reverse('bookings:booking-detail', kwargs={'pk': response.data['id']})
        response1 = self.client.get(detail_url, format='application/json')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data['id'], response.data['id'])

    def test_update_booking(self):
        """Test can update booking."""
        self.url = reverse('bookings:booking-list')
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.data['seat'])
        data = response.data
        data['seat'] = {
            "id": 1,
            "class_group": "Economy",
            "letter": "A",
            "row": 1,
            "booked": False
        }
        detail_url = reverse('bookings:booking-detail', kwargs={'pk': response.data['id']})
        response1 = self.client.put(detail_url, data=data, format='json')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data['id'], response.data['id'])
        self.assertIsNotNone(response1.data['seat'])
        booking = Booking.objects.get(id=response.data['id'])
        self.assertEqual(booking.seat, self.seat1)
        self.seat1.refresh_from_db()
        self.assertEqual(self.seat1.booked, True)

        # test update booking different flight seat
        data = response1.data
        data['seat'] = {
            "id": 2,
            "class_group": "Economy",
            "letter": "B",
            "row": 1,
            "booked": False
        }
        response2 = self.client.put(detail_url, data=data, format='json')
        self.assertEqual(response2.status_code, 200)
        self.assertIsNotNone(response2.data['seat'])
        booking = Booking.objects.get(id=response.data['id'])
        self.assertEqual(booking.seat, self.seat2)
        self.seat1.refresh_from_db()
        self.seat2.refresh_from_db()
        self.assertEqual(self.seat1.booked, False)
        self.assertEqual(self.seat2.booked, True)
