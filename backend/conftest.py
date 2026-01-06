"""
PyTest Configuration and Shared Fixtures

BEGINNER EXPLANATION:
---------------------
This file contains "fixtures" - reusable code that sets up test data.
Think of fixtures as "helpers" that prepare things for your tests.

For example, if every test needs a user, instead of creating a user
in every test file, we create a fixture once here and reuse it.

HOW IT WORKS:
1. Functions decorated with @pytest.fixture are fixtures
2. Tests can "request" fixtures as parameters
3. pytest automatically provides the fixture when the test runs

EXAMPLE:
--------
# In conftest.py:
@pytest.fixture
def test_user():
    return User.objects.create_user(username='testuser', password='testpass')

# In test file:
def test_something(test_user):  # pytest automatically provides test_user
    assert test_user.username == 'testuser'
"""

import pytest
from django.contrib.auth.models import User
from django.test import Client
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def django_db_setup():
    """
    Configure database for tests.
    
    BEGINNER EXPLANATION:
    ---------------------
    This tells pytest-django to use a test database.
    Tests use a separate database that gets created before tests
    and deleted after tests, so your real data stays safe.
    """
    pass


@pytest.fixture
def test_user(db):
    """
    Create a test user for tests.
    
    BEGINNER EXPLANATION:
    ---------------------
    This fixture creates a user that can be used in any test.
    The 'db' parameter tells pytest-django to enable database access.
    
    USAGE:
    ------
    def test_something(test_user):
        # test_user is automatically available
        assert test_user.username == 'testuser'
    """
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def test_user_2(db):
    """
    Create a second test user (useful for testing permissions).
    
    BEGINNER EXPLANATION:
    ---------------------
    Sometimes we need two users to test that users can only see
    their own data. This creates a second user.
    """
    return User.objects.create_user(
        username='testuser2',
        email='test2@example.com',
        password='testpass123'
    )


@pytest.fixture
def api_client():
    """
    Create an API client for making HTTP requests in tests.
    
    BEGINNER EXPLANATION:
    ---------------------
    This is like a web browser for tests - it lets you make
    GET, POST, PUT, DELETE requests to your API.
    
    USAGE:
    ------
    def test_api(api_client, test_user):
        # Make a request to /api/contracts/
        response = api_client.get('/api/contracts/')
        assert response.status_code == 401  # Not authenticated
    """
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, test_user):
    """
    Create an authenticated API client (user is logged in).
    
    BEGINNER EXPLANATION:
    ---------------------
    This creates an API client that's already logged in as test_user.
    This is useful when you need to test endpoints that require login.
    
    USAGE:
    ------
    def test_authenticated_api(authenticated_api_client):
        # This request will be authenticated
        response = authenticated_api_client.get('/api/contracts/')
        assert response.status_code == 200  # OK (authenticated)
    """
    # Get JWT token for the user
    refresh = RefreshToken.for_user(test_user)
    access_token = str(refresh.access_token)
    
    # Add token to API client headers
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    return api_client


@pytest.fixture
def django_client():
    """
    Create a Django test client (for non-API tests).
    
    BEGINNER EXPLANATION:
    ---------------------
    This is a simpler client for testing regular Django views
    (not REST API). We might not use this much since we're using
    REST API, but it's good to have.
    """
    return Client()

