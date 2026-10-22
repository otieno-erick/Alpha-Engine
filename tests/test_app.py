<<<<<<< Updated upstream
from fastapi.testclient import TestClient
=======
﻿from fastapi.testclient import TestClient
>>>>>>> Stashed changes

from alpha_engine.app import app


def test_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "alpha-engine"
    assert payload["rules_loaded"] is True


def test_root_endpoint():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "alpha-engine"
    assert payload["status"] == "ready"


def test_phase1_status_endpoint():
    client = TestClient(app)
    response = client.get("/phase1/status")
    assert response.status_code == 200
    payload = response.json()
    assert payload["scheduler"]["max_slots"] == 10
    assert payload["quota"]["reserve"] == 5
