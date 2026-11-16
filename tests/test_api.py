from fastapi.testclient import TestClient
from app.main import app
from app.schemas import PredictionOutput
import pytest

@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c

sample = {
    "carat": 0.15,
    "color": "E",
    "clarity": "SI2",
    "depth": 35,
    "table": 35,
    "price": 250,
    "x": 3,
    "y": 3,
    "z": 0.5
}

def test_read_main(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World!"}

def test_predict_cut(client):
    response = client.post("/predict_cut",json=sample)
    assert response.status_code == 200
    assert PredictionOutput.model_validate(response.json())

def test_predict_cut_rejects_bad(client):
    bad_sample = {**sample, "x":0}
    response = client.post("/predict_cut",json=bad_sample)
    assert response.status_code == 422

def test_get_cut_prediction_explanation(client):
    response = client.post("/get_cut_prediction_explanation", json=sample)
    assert response.status_code == 200
