import pytest
from django.urls import reverse
from zainoAcademy_app.models import Usuario, TipoUsuario, Periodo

@pytest.mark.django_db
def test_inicio_view(client):
    url = reverse("home")  # corregido
    response = client.get(url)
    assert response.status_code == 200
    assert b"<!DOCTYPE html" in response.content

@pytest.mark.django_db
def test_login_view_success(client):
    tipo = TipoUsuario.objects.create(TusTiposUsuario="Profesor")
    usuario = Usuario.objects.create(
        Us_nombre="Luis",
        Us_contraseña="12345",
        documento="111222",
        genero="masculino",
        correo="luis@test.com",
        TipoUsuario=tipo
    )
    url = reverse("login")
    response = client.post(url, {"correo": "luis@test.com", "contraseña": "12345"})
    assert response.status_code == 302
    assert "usuario_id" in client.session

@pytest.mark.django_db
def test_login_view_fail(client):
    url = reverse("login")
    response = client.post(url, {"correo": "noexiste@test.com", "contraseña": "x"})
    assert response.status_code == 200
    assert "Correo o contraseña incorrectos" in response.content.decode()  # corregido


@pytest.mark.django_db
def test_consultar_periodos(client):
    Periodo.objects.create(Per_nombre="2025-1")
    url = reverse("consultar_periodos")
    response = client.get(url)
    assert response.status_code == 200
    assert "2025-1" in response.content.decode()



#Test con error

@pytest.mark.django_db
def test_dashboard_directivos_requires_login(client):
    url = reverse("dashboard_directivo")  # POSIBLE PROBELMA EN VISTA O URLS
    response = client.get(url)
    assert response.status_code == 302  # requiere login 
    assert reverse("login") in response.url