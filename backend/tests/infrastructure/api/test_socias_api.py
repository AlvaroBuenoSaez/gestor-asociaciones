from fastapi.testclient import TestClient
from app.infrastructure.persistence.models.user_sql import AsociacionVecinalModel
from datetime import date

def test_create_socia(client: TestClient, db_session):
    # 1. Crear asociación
    asociacion = AsociacionVecinalModel(nombre="Asoc Socias", numero_registro="REG-SOC")
    db_session.add(asociacion)
    db_session.commit()
    db_session.refresh(asociacion)

    # 2. Datos socia
    socia_data = {
        "numero_socia": "S001",
        "nombre": "Maria",
        "apellidos": "Garcia",
        "asociacion_id": asociacion.id,
        "fecha_inscripcion": str(date.today())
    }

    # 3. API Call
    response = client.post("/api/v1/socias/", json=socia_data)

    # 4. Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Maria"
    assert data["numero_socia"] == "S001"
    assert data["asociacion_id"] == asociacion.id

def test_list_socias(client: TestClient, db_session):
    # 1. Setup
    asociacion = AsociacionVecinalModel(nombre="Asoc List", numero_registro="REG-LIST")
    db_session.add(asociacion)
    db_session.commit()

    from app.infrastructure.persistence.models.socia_sql import SociaModel
    socia = SociaModel(
        numero_socia="S002",
        nombre="Ana",
        apellidos="Lopez",
        asociacion_id=asociacion.id
    )
    db_session.add(socia)
    db_session.commit()

    # 2. API Call
    response = client.get(f"/api/v1/socias/?asociacion_id={asociacion.id}")

    # 3. Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Ana"
