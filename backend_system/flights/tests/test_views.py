from django.shortcuts import reverse

from rest_framework.test import APITestCase

from authentication.models import User
from flights.models import Location, Flight, Seat


class LocationViewSetTestCase(APITestCase):
    """Test LocationViewset TestCase."""
    def setUp(self):
        self.normal_user = User.objects.create_user(
            email='normal@email.com', password='flightpassword')
        self.staff_user = User.objects.create_user(
            email='staff@email.com', password='flightpassword')
        self.staff_user.is_staff = True
        self.staff_user.save()
        self.super_user = User.objects.create_superuser(
            email='admin@email.com', password='flightpassword')
        self.url = reverse('flights:destination-list')

        self.data = {
            'country': 'Kenya',
            'city': 'Nairobi',
            'airport': 'JKIA'
        }

    def test_add_location(self):
        """Test add location functionality"""
        with self.subTest('Test normal user cannot add location.'):
            self.client.force_authenticate(user=self.normal_user)
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.data['error'], 'PermissionDenied')
            self.assertEqual(response.data['error_description'],
                             'You do not have permission to perform this action.')

        with self.subTest('Test a staff can add location.'):
            self.client.force_authenticate(user=self.staff_user)
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['country'], 'Kenya')
            self.assertEqual(response.data['city'], 'Nairobi')
            self.assertEqual(response.data['airport'], 'Jkia')
            self.assertEqual(Location.objects.all().count(), 1)

        with self.subTest('Test a super user can add location.'):
            data = {
                'country': 'kenya',
                'city': 'nairobi',
                'airport': 'Wilson'
            }
            self.client.force_authenticate(user=self.super_user)
            response = self.client.post(self.url, data=data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['country'], 'Kenya')
            self.assertEqual(response.data['city'], 'Nairobi')
            self.assertEqual(response.data['airport'], 'Wilson')
            self.assertEqual(Location.objects.all().count(), 2)

    def test_can_not_add_duplicate_location(self):
        """Test duplicate locations cannot be added."""
        self.client.force_authenticate(user=self.super_user)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 201)
        count = Location.objects.all().count()
        response2 = self.client.post(self.url, data=self.data)
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.data['error'], 'ValidationError')
        self.assertIn('Location already exists, kindly use existing location.',
                      str(response2.data['error_description']))
        self.assertEqual(Location.objects.all().count(), count)

        # test for data similar to already created loaction but with jumbled cases
        data = {
            'country': 'KenYa',
            'city': 'nairobi',
            'airport': 'jkia'
        }
        response3 = self.client.post(self.url, data=data)
        self.assertEqual(response3.status_code, 400)
        self.assertEqual(response3.data['error'], 'ValidationError')
        self.assertIn('Location already exists, kindly use existing location.',
                      str(response3.data['error_description']))
        self.assertEqual(Location.objects.all().count(), count)

    def test_list_locations(self):
        """Test view all existing locations."""
        location1 = Location.objects.create(
            country='Kenya',
            city='Nairobi',
            airport='JKIA'
        )
        location2 = Location.objects.create(
            country='France',
            city='Paris',
            airport='gaulle'
        )
        # test normal users can see locations
        self.client.force_authenticate(user=self.normal_user)
        response1 = self.client.get(self.url, format='application/json')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(response1.data), 2)
        self.assertIn(location1.city, str(response1.data))
        self.assertIn(location2.city, str(response1.data))
        # test staff and superusers can view locations
        self.client.force_authenticate(user=self.staff_user)
        response2 = self.client.get(self.url, format='application/json')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(response2.data), 2)

    def test_retrieve_location(self):
        """Test a single location can be retrieved."""
        # create location
        self.client.force_authenticate(user=self.super_user)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 201)
        detail_url = reverse('flights:destination-detail', kwargs={'pk': response.data['id']})
        # test normal users can retrieve location
        self.client.force_authenticate(user=self.normal_user)
        response1 = self.client.get(detail_url, format='application/json')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data['id'], response.data['id'])
        # test staff and superusers can view location
        self.client.force_authenticate(user=self.staff_user)
        response2 = self.client.get(detail_url, format='application/json')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data['id'], response.data['id'])

    def test_update_location(self):
        """Test update location functionality."""
        with self.subTest('Test staff can update location'):
            # create location
            self.client.force_authenticate(user=self.super_user)
            response = self.client.post(self.url, data=self.data)
            self.assertEqual(response.status_code, 201)
            detail_url = reverse('flights:destination-detail', kwargs={'pk': response.data['id']})
            new_data = response.data
            new_data['airport'] = 'newport'
            # update location
            response2 = self.client.put(detail_url, data=new_data)
            self.assertEqual(response2.status_code, 200)
            self.assertEqual(response2.data['airport'], 'Newport')

            # test update location with same data raises an error
            new_data['airport'] = 'newport'
            response3 = self.client.put(detail_url, data=new_data)
            self.assertEqual(response3.status_code, 400)
            self.assertIn('Location already exists, kindly use existing location', str(response3.data))

            # test normal user cannot update location
            self.client.force_authenticate(user=self.normal_user)
            new_data['airport'] = 'Try'
            response4 = self.client.put(detail_url, data=new_data)
            self.assertEqual(response4.status_code, 403)
            self.assertEqual(response4.data['error'], 'PermissionDenied')
            self.assertIn('You do not have permission to perform this action', str(response4.data['error_description']))
            # confirm location airport was not changed
            response5 = self.client.get(detail_url, data=new_data)
            self.assertEqual(response5.status_code, 200)
            self.assertEqual(response5.data['airport'], response2.data['airport'])
            self.assertNotEqual(response5.data['airport'], 'Try')


class FlightViewSetTestCase(APITestCase):
    """Test FlightViewSet TestCase."""
    def setUp(self):
        self.normal_user = User.objects.create_user(
            email='normal@email.com', password='flightpassword')
        self.staff_user = User.objects.create_user(
            email='staff@email.com', password='flightpassword')
        self.staff_user.is_staff = True
        self.staff_user.save()
        self.super_user = User.objects.create_superuser(
            email='admin@email.com', password='flightpassword')
        self.url = reverse('flights:flight-list')

        self.location1 = Location.objects.create(
            country='Kenya',
            city='Nairobi',
            airport='JKIA'
        )
        self.location2 = Location.objects.create(
            country='France',
            city='Paris',
            airport='gaulle'
        )
        self.data = {
            'name': 'Flight valeria',
            'origin': {
                'id': self.location1.id,
                'country': self.location1.country,
                'city': self.location1.city,
                'airport': self.location1.airport
            },
            'destination': {
                'id': self.location2.id,
                'country': self.location2.country,
                'city': self.location2.city,
                'airport': self.location2.airport
            }
        }

    def test_add_flight_functionality(self):
        """Test add flight functionality."""
        with self.subTest('Test normal user cannot add flight.'):
            self.client.force_authenticate(user=self.normal_user)
            response = self.client.post(self.url, data=self.data, format='json')
            self.assertEqual(response.status_code, 403)
            self.assertEqual(response.data['error'], 'PermissionDenied')
            self.assertEqual(response.data['error_description'],
                             'You do not have permission to perform this action.')

        with self.subTest('Test a staff can add flight.'):
            self.client.force_authenticate(user=self.staff_user)
            response = self.client.post(self.url, data=self.data, format='json')
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], 'FLIGHT VALERIA')
            self.assertEqual(Flight.objects.all().count(), 1)

        with self.subTest('Test a super user can add location.'):
            self.data['name'] = 'flight1'
            self.client.force_authenticate(user=self.super_user)
            response = self.client.post(self.url, data=self.data, format='json')
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], 'FLIGHT1')
            self.assertEqual(Location.objects.all().count(), 2)

    def test_cannot_add_duplicate_flight_no_departure_time(self):
        """Flight with similar name and departure time to existing one cannot be added."""
        self.client.force_authenticate(user=self.staff_user)
        response1 = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response1.status_code, 201)
        response2 = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.data['error'], 'ValidationError')
        self.assertIn(
            'Flight with same name exists, schedule existing flight.',
            str(response2.data['error_description']))
        # confirm we just have one Flight in the system
        self.assertEqual(Flight.objects.all().count(), 1)

    def test_flight_origin_and_destination_should_not_be_similar(self):
        """Test that flight origin and destination have to be different."""
        self.data['destination'] = self.data['origin']
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'ValidationError')
        self.assertIn(
            'Flight origin and destination can not be the same.',
            str(response.data['error_description']))
        # confirm flight was not created
        self.assertEqual(Flight.objects.all().count(), 0)

    def test_invalid_origin_or_destination_given(self):
        """Test flight not created invalid location."""
        self.data['destination'] = {
            'country': 'countr1',
            'city': 'city1',
            'airport': 'airport1'
        }
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'ValidationError')
        self.assertIn(
            'Origin/destination given is not in the allowed destinations.',
            str(response.data['error_description']))
        # confirm flight was not created
        self.assertEqual(Flight.objects.all().count(), 0)


class SeatViewsetTestCase(APITestCase):
    pass
