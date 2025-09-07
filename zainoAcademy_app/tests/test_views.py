import pytest
from django.urls import reverse

@pytest.mark.django_db
def test_login_page_loads(client):
    url = reverse('login')
    response = client.get(url)
    assert response.status_code == 200
    assert b"login" in response.content.lower()
    