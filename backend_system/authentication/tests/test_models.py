from django.db.utils import IntegrityError
from django.test import TestCase

from authentication.models import User, Token


class UserModelTestCase(TestCase):
    # TO DO: Create BaseTestCase
    def setUp(self):
        self.user = User.objects.create_user(
            email='flightsystem@email.com', password='flightpassword')

    def test_user_created_successfully(self):
        self.assertEqual(User.objects.all().count(), 1)

    def test_uplicate_user_fails(self):
        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email='flightsystem@email.com', password='flightpassword')


class TokenModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='flightsystem@email.com', password='flightpassword')

    def test_user_token_saved_successfully(self):
        self.assertEqual(Token.objects.all().count(), 1)

    def test_saving_user_token_fails_invalid_user(self):
        with self.assertRaises(User.DoesNotExist):
            Token.objects.create(user=User.objects.get(email='invalid@email.com'),
                                 key='Token thiswillfail123')
