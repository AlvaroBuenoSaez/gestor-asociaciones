from fastapi.testclient import TestClient
from app.infrastructure.persistence.models.user_sql import AsociacionVecinalModel

def test_create_user(client: TestClient, db_session):
    # 1. Crear una asociación previa (necesaria por la FK)
    asociacion = AsociacionVecinalModel(
        nombre="Asociación Test",
        numero_registro="REG-001"
    )
    db_session.add(asociacion)
    db_session.commit()
    db_session.refresh(asociacion)

    # 2. Datos del usuario a crear
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword",
        "first_name": "Test",
        "last_name": "User",
        "role": "member",
        "asociacion_id": asociacion.id
    }

    # 3. Llamada a la API
    response = client.post("/api/v1/users/", json=user_data)

    # 4. Aserciones
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert data["profile"]["role"] == "member"
    assert data["profile"]["asociacion_id"] == asociacion.id

def test_list_users_by_association(client: TestClient, db_session):
    # 1. Setup: Crear asociación y usuario
    asociacion = AsociacionVecinalModel(nombre="Asoc 1", numero_registro="R1")
    db_session.add(asociacion)
    db_session.commit()

    # Crear usuario vía API para reutilizar lógica o directamente en DB
    # Vamos a hacerlo directo en DB para variar y probar el GET aisladamente
    from app.infrastructure.persistence.models.user_sql import UserModel, UserProfileModel

    user = UserModel(username="user1", email="u1@test.com", is_active=True)
    db_session.add(user)
    db_session.commit()

    profile = UserProfileModel(user_id=user.id, asociacion_id=asociacion.id, role="admin")
    db_session.add(profile)
    db_session.commit()

    # 2. Llamada a la API
    response = client.get(f"/api/v1/users/?asociacion_id={asociacion.id}")

    # 3. Aserciones
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["username"] == "user1"
    assert data[0]["profile"]["role"] == "admin"
