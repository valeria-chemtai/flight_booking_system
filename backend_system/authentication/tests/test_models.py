from django.db.utils import IntegrityError
from django.test import TestCase

from authentication.models import User


class UserModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='flightsystem@email.com', password='flightpassword')

    def test_user_created_successfully(self):
        self.assertEqual(User.objects.all().count(), 1)

    def test_uplicate_user_fails(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='flightsystem@email.com', password='flightpassword')
