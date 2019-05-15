from django.shortcuts import reverse

from rest_framework.test import APITestCase

from authentication.models import User, Token


class UserSignupViewsetTestCase(APITestCase):
    """UserSignup viewset TestCase."""
    def setUp(self):
        self.url = reverse('authentication:signup')

    def test_user_signup_successful(self):
        """Test user signup successful."""
        data = {
            'email': 'user@app.com',
            'first_name': 'test',
            'last_name': 'user',
            'password': 'test_password1'
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['message'], 'User successfully registered.')

    def test_user_signup_existing_email(self):
        """Test user signup unsuccessful for already signed user."""
        data = {
            'email': 'user@app.com',
            'first_name': 'test',
            'last_name': 'user',
            'password': 'test_password1'
        }
        response1 = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response1.status_code, 201)
        response2 = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response2.status_code, 400)
        self.assertIn('A user with this email address exists', str(response2.data))

    def test_user_signup_no_password(self):
        """Test user signup fails if password not provided."""
        data = {
            'email': 'user@app.com',
            'first_name': 'test',
            'last_name': 'user'
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'ValidationError')


class UserSignInViewTestCase(APITestCase):
    """Test user signin view."""
    def setUp(self):
        self.signup_url = reverse('authentication:signup')
        self.url = reverse('authentication:sign-in')

    def test_user_sign_in_successful(self):
        """Test user sign-in successful."""
        # signup user first
        data = {
            'email': 'user@app.com',
            'first_name': 'test',
            'last_name': 'user',
            'password': 'test_password1'
        }
        response1 = self.client.post(self.signup_url, data=data, format='json')
        self.assertEqual(response1.status_code, 201)

        # sign_in user
        data = {
            'email': 'user@app.com',
            'password': 'test_password1'
        }
        response2 = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response2.status_code, 200)
        self.assertIn('token', str(response2.data))

    def test_user_sign_in_wrong_password(self):
        """Test user sign in fails invalid password."""
        # signup user first
        data = {
            'email': 'user@app.com',
            'first_name': 'test',
            'last_name': 'user',
            'password': 'test_password1'
        }
        response1 = self.client.post(self.signup_url, data=data, format='json')
        self.assertEqual(response1.status_code, 201)

        # sign_in user
        data = {
            'email': 'user@app.com',
            'password': 'wrong_password1'
        }
        response2 = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response2.status_code, 400)
        self.assertIn('Invalid email/password Combination.', str(response2.data))

    def test_user_sign_in_unsuccessful_user_not_registered(self):
        """Test user sign in fails user not registered."""
        # sign_in unregistered user
        data = {
            'email': 'user@app.com',
            'password': 'test_password1'
        }
        response = self.client.post(self.url, data=data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('User not registered. Please signup first.', str(response.data))


class UserProfileViewsetTestCase(APITestCase):
    """UserProfileViewset Tests."""
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@app.com',
            first_name='test',
            last_name='user',
            password='test_password1'
        )
        self.user2 = User.objects.create_user(
            email='user2@app.com',
            first_name='test1',
            last_name='user1',
            password='test_password2'
        )

    def test_users_list(self):
        """Test list users successful for authenticated user."""
        self.client.force_authenticate(user=self.user)
        self.url = reverse('authentication:users-list')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    def test_users_list_fail_unauthenticated_user(self):
        """Test list users unsuccessful for unauthenticated user."""
        self.url = reverse('authentication:users-list')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['error'], 'NotAuthenticated')

    def test_user_retrieve(self):
        """Test retrieve user successful for authenticated user."""
        self.client.force_authenticate(user=self.user)
        self.url = reverse('authentication:user-detail', kwargs={'pk': self.user.pk})
        expected_result = {
            'pk': self.user.pk,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'date_joined': self.user.date_joined.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            'is_active': self.user.is_active,
            'is_staff': self.user.is_staff,
            'is_superuser': self.user.is_superuser,
            'passport_photo': self.user.passport_photo
        }
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, expected_result)


class UserChangePasswordViewTestCase(APITestCase):
    """UserChangePasswordView Tests."""
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@app.com',
            first_name='test',
            last_name='user',
            password='test_password1'
        )
        self.data = {
            'old_password': 'test_password1',
            'new_password': 'New_password2',
            'confirm_new_password': 'New_password2'
        }

    def test_user_password_change_fails_unauthenticated_user(self):
        """Test change password fails unauthenticated user."""
        self.url = reverse('authentication:change-password')
        response = self.client.post(self.url, data=self.data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['error'], 'NotAuthenticated')

    def test_user_password_change_fails_new_password_and_confirm_password_unmatch(self):
        """Test change password fails for unmatching new_password and confirm_new_password."""
        self.client.force_authenticate(user=self.user)
        self.url = reverse('authentication:change-password')
        data = {
            'old_password': 'test_password1',
            'new_password': 'New_password2',
            'confirm_new_password': 'New_password'
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'ValidationError')
        self.assertIn('Passwords do not match.', str(response.data))

    def test_password_change_successful(self):
        """Test change password successful."""
        self.client.force_authenticate(user=self.user)
        self.url = reverse('authentication:change-password')
        old_token = Token.objects.get(user=self.user).key
        response = self.client.post(self.url, data=self.data)
        new_token = Token.objects.get(user=self.user).key
        self.assertEqual(response.status_code, 200)
        self.assertIn(new_token, str(response.data))
        # confirm token changes
        self.assertNotEqual(old_token, new_token)
