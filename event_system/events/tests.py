from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import Event, Registration


class AuthenticationTests(APITestCase):
    """Test user registration and login endpoints."""

    def test_user_registration(self):
        """Test that a new user can register successfully."""
        url = '/api/auth/register/'
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'TestPass123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User registered successfully')
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_registration_password_mismatch(self):
        """Test that registration fails when passwords don't match."""
        url = '/api/auth/register/'
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123!',
            'password_confirm': 'DifferentPass123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_login(self):
        """Test that a user can login and receive tokens."""
        # Create user first
        user = User.objects.create_user(username='testuser', password='TestPass123!')
        
        url = '/api/auth/login/'
        data = {'username': 'testuser', 'password': 'TestPass123!'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class EventTests(APITestCase):
    """Test event listing and detail endpoints."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username='testuser', password='TestPass123!')
        self.event = Event.objects.create(
            title='Test Event',
            description='A test event',
            location='Test Location',
            date_time=timezone.now() + timedelta(days=10),
            capacity=100,
            created_by=self.user
        )

    def test_list_events(self):
        """Test that events can be listed without authentication."""
        url = '/api/events/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Event')

    def test_list_events_with_search(self):
        """Test searching events by title."""
        url = '/api/events/?search=Test'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_list_events_upcoming_filter(self):
        """Test filtering for upcoming events."""
        # Create a past event
        past_event = Event.objects.create(
            title='Past Event',
            description='A past event',
            location='Test Location',
            date_time=timezone.now() - timedelta(days=10),
            capacity=50,
            created_by=self.user
        )
        
        url = '/api/events/?upcoming=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Event')

    def test_event_detail(self):
        """Test retrieving a single event."""
        url = f'/api/events/{self.event.id}/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Event')
        self.assertEqual(response.data['seats_left'], 100)


class RegistrationTests(APITestCase):
    """Test event registration functionality."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(username='testuser', password='TestPass123!')
        self.event = Event.objects.create(
            title='Test Event',
            description='A test event',
            location='Test Location',
            date_time=timezone.now() + timedelta(days=10),
            capacity=100,
            created_by=self.user
        )
        # Authenticate user
        self.client.force_authenticate(user=self.user)

    def test_successful_registration(self):
        """Test that a user can successfully register for an event."""
        url = f'/api/events/{self.event.id}/register/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'Registration successful.')
        self.assertTrue(Registration.objects.filter(user=self.user, event=self.event).exists())
        
        # Check that seats_left decreased
        self.event.refresh_from_db()
        self.assertEqual(self.event.seats_left, 99)

    def test_duplicate_registration_blocked(self):
        """Test that duplicate registrations are blocked."""
        url = f'/api/events/{self.event.id}/register/'
        
        # First registration
        response1 = self.client.post(url)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second registration (should fail)
        response2 = self.client.post(url)
        self.assertEqual(response2.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response2.data['detail'], 'You are already registered for this event.')

    def test_full_event_blocked(self):
        """Test that registration is blocked when event is full."""
        # Create an event with capacity 1
        small_event = Event.objects.create(
            title='Small Event',
            description='A small event',
            location='Test Location',
            date_time=timezone.now() + timedelta(days=10),
            capacity=1,
            created_by=self.user
        )
        
        # Register another user
        other_user = User.objects.create_user(username='otheruser', password='TestPass123!')
        Registration.objects.create(user=other_user, event=small_event, status='confirmed')
        
        # Try to register (should fail)
        url = f'/api/events/{small_event.id}/register/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'This event is fully booked.')

    def test_past_event_blocked(self):
        """Test that registration is blocked for past events."""
        past_event = Event.objects.create(
            title='Past Event',
            description='A past event',
            location='Test Location',
            date_time=timezone.now() - timedelta(days=10),
            capacity=100,
            created_by=self.user
        )
        
        url = f'/api/events/{past_event.id}/register/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['detail'], 'Cannot register for past events.')


class RegistrationManagementTests(APITestCase):
    """Test registration management (view and cancel)."""

    def setUp(self):
        """Set up test data."""
        self.user1 = User.objects.create_user(username='user1', password='TestPass123!')
        self.user2 = User.objects.create_user(username='user2', password='TestPass123!')
        self.event = Event.objects.create(
            title='Test Event',
            description='A test event',
            location='Test Location',
            date_time=timezone.now() + timedelta(days=10),
            capacity=100,
            created_by=self.user1
        )
        self.registration = Registration.objects.create(
            user=self.user1,
            event=self.event,
            status='confirmed'
        )

    def test_list_own_registrations(self):
        """Test that a user can list their own registrations."""
        self.client.force_authenticate(user=self.user1)
        url = '/api/registrations/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'user1')

    def test_cancelling_frees_seat(self):
        """Test that cancelling a registration frees the seat."""
        self.client.force_authenticate(user=self.user1)
        
        # Initial seats_left
        initial_seats = self.event.seats_left
        self.assertEqual(initial_seats, 99)
        
        # Cancel registration
        url = f'/api/registrations/{self.registration.id}/cancel/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['detail'], 'Registration cancelled successfully.')
        
        # Check that seats_left increased
        self.event.refresh_from_db()
        self.assertEqual(self.event.seats_left, 100)
        
        # Check registration status
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.status, 'cancelled')

    def test_user_cannot_cancel_others_registration(self):
        """Test that a user cannot cancel someone else's registration."""
        self.client.force_authenticate(user=self.user2)
        
        url = f'/api/registrations/{self.registration.id}/cancel/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'You can only cancel your own registrations.')

    def test_re_registration_after_cancellation(self):
        """Test that a user can re-register after cancelling."""
        self.client.force_authenticate(user=self.user1)
        
        # Cancel registration
        url = f'/api/registrations/{self.registration.id}/cancel/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Re-register
        register_url = f'/api/events/{self.event.id}/register/'
        response = self.client.post(register_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['detail'], 'Registration reactivated successfully.')
        
        # Check status is confirmed
        self.registration.refresh_from_db()
        self.assertEqual(self.registration.status, 'confirmed')

