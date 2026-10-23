# Testing Guide

## Running Tests

### Run All Tests
```bash
cd event_system
../venv/Scripts/python manage.py test events
```

### Run Specific Test Class
```bash
../venv/Scripts/python manage.py test events.tests.AuthenticationTests
```

### Run Specific Test Method
```bash
../venv/Scripts/python manage.py test events.tests.AuthenticationTests.test_user_registration
```

### Run with Verbose Output
```bash
../venv/Scripts/python manage.py test events --verbosity=2
```

### Run with Coverage (if coverage is installed)
```bash
../venv/Scripts/pip install coverage
../venv/Scripts/coverage run --source='.' manage.py test events
../venv/Scripts/coverage report
```

## Test Coverage

### AuthenticationTests (3 tests)
- ✅ test_user_registration - Successful user registration
- ✅ test_user_registration_password_mismatch - Registration fails with password mismatch
- ✅ test_user_login - User login and token generation

### EventTests (4 tests)
- ✅ test_list_events - List all events without authentication
- ✅ test_list_events_with_search - Search events by title
- ✅ test_list_events_upcoming_filter - Filter for upcoming events only
- ✅ test_event_detail - Retrieve single event details

### RegistrationTests (4 tests)
- ✅ test_successful_registration - User can register for an event
- ✅ test_duplicate_registration_blocked - Duplicate registrations are blocked (409)
- ✅ test_full_event_blocked - Registration blocked when event is full (400)
- ✅ test_past_event_blocked - Registration blocked for past events (400)

### RegistrationManagementTests (4 tests)
- ✅ test_list_own_registrations - User can list their own registrations
- ✅ test_cancelling_frees_seat - Cancelling frees the seat (seats_left increases)
- ✅ test_user_cannot_cancel_others_registration - User cannot cancel others' registrations (403)
- ✅ test_re_registration_after_cancellation - User can re-register after cancellation

## Test Results

All 15 tests passed successfully in 13.654s.

## Test Database

Django automatically creates a separate test database for testing:
- Test database is created before tests run
- Test database is destroyed after tests complete
- Tests don't affect your development database

## Adding New Tests

To add new tests, edit `event_system/events/tests.py` and follow the pattern:

```python
class YourTestClass(APITestCase):
    def setUp(self):
        # Set up test data
        pass

    def test_your_test_case(self):
        # Your test logic
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

## Best Practices

1. **One test per method**: Each test method should test one specific thing
2. **Descriptive names**: Use clear, descriptive test method names
3. **Setup and teardown**: Use `setUp()` for common test data
4. **Authentication**: Use `self.client.force_authenticate(user=self.user)` for authenticated requests
5. **Assertions**: Use appropriate assertions (assertEqual, assertTrue, etc.)
