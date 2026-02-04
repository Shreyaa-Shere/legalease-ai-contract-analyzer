"""
PyTest Configuration and Shared Fixtures

This file contains reusable fixtures for setting up test data.
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
    Tests use a separate database that gets created before tests
    and deleted after tests.
    """
    pass


@pytest.fixture
def test_user(db):
    """
    Create a test user for tests.
    The 'db' parameter tells pytest-django to enable database access.
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
    """
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, test_user):
    """
    Create an authenticated API client (user is logged in).
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
    """
    return Client()

