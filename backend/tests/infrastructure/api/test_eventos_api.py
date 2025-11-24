from fastapi.testclient import TestClient
from app.infrastructure.persistence.models.user_sql import AsociacionVecinalModel
from app.infrastructure.persistence.models.socia_sql import SociaModel
from datetime import datetime, timedelta

def test_create_evento(client: TestClient, db_session):
    # 1. Setup: Asociacion y Responsable (Socia)
    asociacion = AsociacionVecinalModel(nombre="Asoc Eventos", numero_registro="REG-EVT")
    db_session.add(asociacion)
    db_session.commit()

    socia = SociaModel(
        numero_socia="S003",
        nombre="Laura",
        apellidos="Perez",
        asociacion_id=asociacion.id
    )
    db_session.add(socia)
    db_session.commit()
    db_session.refresh(socia)

    # 2. Datos evento
    evento_data = {
        "nombre": "Fiesta Verano",
        "fecha": datetime.now().isoformat(),
        "duracion": str(timedelta(hours=2).total_seconds()), # Pydantic expects seconds or ISO duration?
        # Pydantic v2 timedelta: expects float (seconds) or ISO string.
        # Let's pass float seconds.
        "asociacion_id": asociacion.id,
        "responsable_id": socia.id
    }
    # Fix: Pydantic timedelta serialization/deserialization.
    # If we pass float, it's seconds.
    evento_data["duracion"] = 7200.0 # 2 hours

    # 3. API Call
    response = client.post("/api/v1/eventos/", json=evento_data)

    # 4. Assertions
    if response.status_code != 201:
        print(response.json())
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Fiesta Verano"
    assert data["responsable_id"] == socia.id
    # Check duration returned (Pydantic serializes timedelta to ISO string usually in v2, or float?)
    # Default serialization for timedelta is ISO 8601 duration string (P0DT2H0M0S) or seconds depending on config.
    # Let's check what we get.
    assert data["duracion"] is not None

def test_list_eventos(client: TestClient, db_session):
    # 1. Setup
    asociacion = AsociacionVecinalModel(nombre="Asoc Evt List", numero_registro="REG-EVT-L")
    db_session.add(asociacion)
    db_session.commit()

    socia = SociaModel(numero_socia="S004", nombre="Elena", apellidos="Ruiz", asociacion_id=asociacion.id)
    db_session.add(socia)
    db_session.commit()

    from app.infrastructure.persistence.models.evento_sql import EventoModel
    evento = EventoModel(
        nombre="Taller",
        fecha=datetime.now(),
        asociacion_id=asociacion.id,
        responsable_id=socia.id,
        duracion=3600000000 # 1 hour in microseconds
    )
    db_session.add(evento)
    db_session.commit()

    # 2. API Call
    response = client.get(f"/api/v1/eventos/?asociacion_id={asociacion.id}")

    # 3. Assertions
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["nombre"] == "Taller"
