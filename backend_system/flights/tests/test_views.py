from django.utils import timezone
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
        # create location
        self.client.force_authenticate(user=self.super_user)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 201)
        detail_url = reverse('flights:destination-detail', kwargs={'pk': response.data['id']})
        new_data = response.data
        with self.subTest('Test staff can update location'):
            new_data['airport'] = 'newport'
            # update location
            response2 = self.client.put(detail_url, data=new_data)
            self.assertEqual(response2.status_code, 200)
            self.assertEqual(response2.data['airport'], 'Newport')

        with self.subTest('Test update location with same data raises an error'):
            new_data['airport'] = 'newport'
            response3 = self.client.put(detail_url, data=new_data)
            self.assertEqual(response3.status_code, 400)
            self.assertIn('Location already exists, kindly use existing location', str(response3.data))

        with self.subTest('Test normal user cannot update location'):
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

    def test_delete_location(self):
        """Test delete location"""
        # create location
        self.client.force_authenticate(user=self.super_user)
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 201)
        detail_url = reverse('flights:destination-detail', kwargs={'pk': response.data['id']})
        # test normal users can not delete location
        self.client.force_authenticate(user=self.normal_user)
        response1 = self.client.delete(detail_url, format='json')
        self.assertEqual(response1.status_code, 403)
        self.assertEqual(response1.data['error'], 'PermissionDenied')
        # test staff not superuser cannot delete location
        self.client.force_authenticate(user=self.staff_user)
        response2 = self.client.delete(detail_url, format='json')
        self.assertEqual(response2.status_code, 403)
        self.assertEqual(response2.data['error'], 'PermissionDenied')

        # test location not deleted by normal user or staff
        self.assertEqual(Location.objects.all().count(), 1)

        # test superuser can delete location
        self.client.force_authenticate(user=self.super_user)
        response3 = self.client.delete(detail_url, format='json')
        self.assertEqual(response3.status_code, 204)

        # test location indeed deleted by superuser
        self.assertEqual(Location.objects.all().count(), 0)


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

        with self.subTest('Test a super user can add flight.'):
            self.data['name'] = 'flight1'
            self.client.force_authenticate(user=self.super_user)
            response = self.client.post(self.url, data=self.data, format='json')
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.data['name'], 'FLIGHT1')
            self.assertEqual(Location.objects.all().count(), 2)

    def test_cannot_add_duplicate_flight_no_departure_time(self):
        """Flight with similar name to an existing unscheduled flight."""
        self.client.force_authenticate(user=self.staff_user)
        # add first flight
        response1 = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response1.status_code, 201)
        # add another flight similar to first one
        response2 = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.data['error'], 'ValidationError')
        self.assertIn(
            'Flight with same name exists, schedule existing flight.',
            str(response2.data['error_description']))
        # confirm we just have one Flight in the system
        self.assertEqual(Flight.objects.all().count(), 1)

    def test_cannot_add_duplicate_flight_with_departure_time(self):
        """Flight with similar name and departure time to existing one cannot be added."""
        self.data['departure_time'] = timezone.now() + timezone.timedelta(hours=2)
        self.client.force_authenticate(user=self.staff_user)
        # add flight
        response1 = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response1.status_code, 201)
        # try yo add second flight with similar data
        response2 = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response2.status_code, 400)
        self.assertEqual(response2.data['error'], 'ValidationError')
        self.assertIn(
            'Flight with same name is already scheduled for a trip at same departure time.',
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

    def test_invalid_destination_given(self):
        """Test flight not created invalid destination location."""
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
            'Destination given is not in the allowed destinations.',
            str(response.data['error_description']))
        # confirm flight was not created
        self.assertEqual(Flight.objects.all().count(), 0)

    def test_invalid_origin_given(self):
        """Test flight not created invalid origin location."""
        self.data['origin'] = {
            'country': 'countr1',
            'city': 'city1',
            'airport': 'airport1'
        }
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'ValidationError')
        self.assertIn(
            'Origin given is not in the allowed destinations.',
            str(response.data['error_description']))
        # confirm flight was not created
        self.assertEqual(Flight.objects.all().count(), 0)

    def test_departure_time_cannot_be_same_as_arrival_time(self):
        """Test departure and arrival times should be different."""
        time = timezone.now() + timezone.timedelta(hours=2)
        self.data['departure_time'] = time
        self.data['arrival_time'] = time
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'ValidationError')
        self.assertIn(
            'Departure time and arrival time cannot be the same.',
            str(response.data['error_description']))
        # confirm flight was not created
        self.assertEqual(Flight.objects.all().count(), 0)

    def test_retrieve_flight(self):
        """Test get single flight"""
        # create flight
        self.client.force_authenticate(user=self.super_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 201)
        detail_url = reverse('flights:flight-detail', kwargs={'pk': response.data['id']})
        # test normal users can retrieve flight
        self.client.force_authenticate(user=self.normal_user)
        response1 = self.client.get(detail_url, format='json')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response1.data['id'], response.data['id'])
        # test staff and superusers can retrieve flight
        self.client.force_authenticate(user=self.staff_user)
        response2 = self.client.get(detail_url, format='json')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response2.data['id'], response.data['id'])

    def test_list_available_flights(self):
        """Test list all flights."""
        flight1 = Flight.objects.create(
            name='FLIGHT1',
            gate='G20',
            created_by=self.super_user
        )
        flight2 = Flight.objects.create(
            name='FLIGHT2',
            gate='G20',
            created_by=self.super_user
        )
        # test normal users can see available flights
        self.client.force_authenticate(user=self.normal_user)
        response1 = self.client.get(self.url, format='application/json')
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(len(response1.data), 2)
        self.assertIn(flight1.name, str(response1.data))
        self.assertIn(flight2.name, str(response1.data))
        # test staff and superusers can view locations
        self.client.force_authenticate(user=self.staff_user)
        response2 = self.client.get(self.url, format='application/json')
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(len(response2.data), 2)

    def test_update_flight(self):
        """Test update flight functionality."""
        # create location
        self.client.force_authenticate(user=self.super_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertIsNone(response.data['departure_time'])
        detail_url = reverse('flights:flight-detail', kwargs={'pk': response.data['id']})
        new_data = response.data
        with self.subTest('Test staff can update flight.'):
            time = timezone.now() + timezone.timedelta(hours=2)
            new_data['departure_time'] = time
            new_data['gate'] = '3c'
            # update flight
            response1 = self.client.put(detail_url, data=new_data, format='json')
            self.assertEqual(response1.status_code, 200)
            self.assertEqual(response1.data['departure_time'],
                             new_data['departure_time'].strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
            # confirm flight was updated
            response2 = self.client.get(detail_url)
            self.assertEqual(response2.status_code, 200)
            self.assertEqual(response2.data['departure_time'],
                             new_data['departure_time'].strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
            self.assertEqual(response2.data['gate'], new_data['gate'].upper())

        with self.subTest('Test update flight will fail if departure_time and arrival time is same'):
            time = timezone.now() + timezone.timedelta(hours=2)
            new_data['departure_time'] = time
            new_data['arrival_time'] = time
            response3 = self.client.put(detail_url, data=new_data, format='json')
            self.assertEqual(response3.status_code, 400)
            self.assertIn('Departure time and arrival time cannot be the same.',
                          str(response3.data))
            # confirm flight was not updated
            response4 = self.client.get(detail_url)
            self.assertEqual(response4.status_code, 200)
            self.assertNotEqual(response4.data['departure_time'],
                                new_data['departure_time'].strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
            self.assertNotEqual(response4.data['arrival_time'],
                                new_data['arrival_time'].strftime('%Y-%m-%dT%H:%M:%S.%fZ'))

        with self.subTest('Test normal user cannot update flight'):
            self.client.force_authenticate(user=self.normal_user)
            new_data['gate'] = '3a'
            response5 = self.client.put(detail_url, data=new_data, format='json')
            self.assertEqual(response5.status_code, 403)
            self.assertEqual(response5.data['error'], 'PermissionDenied')
            self.assertIn('You do not have permission to perform this action',
                          str(response5.data['error_description']))
            # confirm flight gate was not changed
            response6 = self.client.get(detail_url)
            self.assertEqual(response6.status_code, 200)
            self.assertEqual(response6.data['gate'], response2.data['gate'])
            self.assertNotEqual(response6.data['gate'], new_data['gate'].upper())

    def test_delete_flight(self):
        # create flight
        self.client.force_authenticate(user=self.super_user)
        response = self.client.post(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, 201)
        detail_url = reverse('flights:flight-detail', kwargs={'pk': response.data['id']})
        # test normal users can not delete flight
        self.client.force_authenticate(user=self.normal_user)
        response1 = self.client.delete(detail_url, format='json')
        self.assertEqual(response1.status_code, 403)
        self.assertEqual(response1.data['error'], 'PermissionDenied')
        # test staff not superuser cannot delete flight
        self.client.force_authenticate(user=self.staff_user)
        response2 = self.client.delete(detail_url, format='json')
        self.assertEqual(response2.status_code, 403)
        self.assertEqual(response2.data['error'], 'PermissionDenied')

        # test flight not deleted by normal user or staff
        self.assertEqual(Flight.objects.all().count(), 1)

        # test superuser can delete flight
        self.client.force_authenticate(user=self.super_user)
        response3 = self.client.delete(detail_url, format='json')
        self.assertEqual(response3.status_code, 204)

        # test flight indeed deleted by superuser
        self.assertEqual(Flight.objects.all().count(), 0)


class SeatViewsetTestCase(APITestCase):
    pass
