"""Shared fixtures for learn-hub tests."""

import pytest


@pytest.fixture()
def anon_client(client):
    """Unauthenticated Django test client."""
    return client


@pytest.fixture()
def auth_client(client, django_user_model):
    """Authenticated Django test client."""
    user = django_user_model.objects.create_user(
        username="testuser", password="testpass123"
    )
    client.force_login(user)
    client._user = user
    return client
